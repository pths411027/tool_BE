import io
import urllib
from datetime import datetime
from enum import Enum
from io import BytesIO
from typing import List
from urllib.parse import quote

import pandas as pd
from dotenv import load_dotenv
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    FastAPI,
    File,
    HTTPException,
    Query,
    status,
    UploadFile,
)
from sqlalchemy import and_, case, func, or_
from sqlalchemy.orm import aliased
from starlette.responses import StreamingResponse

from app.database.sqlalchemy import Session
from app.routers.user.utils import get_current_user
from app.routers.work_load.BE_tool_func import process_file, process_file_excel
from app.schemas.WL import (
    WLData,
    WLFile,
    WLMainProject,
    WLMember,
    WLOption_Answer,
    WLTeam,
    WLLog,
    WLKPI,
)

# add team
from .request_model import AddMainProject, AddTeam, SubmitRequest, SubmitTask, SubmitKPI

load_dotenv()
app = FastAPI()
work_load_router = APIRouter(tags=["Work Load"], prefix="/work-load")


@work_load_router.get("/home")
async def pm_server_home():
    return {"work_load_router": "home"}


@work_load_router.get("/team-list", status_code=status.HTTP_200_OK)
async def get_team_list():
    with Session() as session:
        results = (
            session.query(
                WLTeam.team_id,
                WLTeam.team_name,
                func.count(WLMember.member_id).label("member_count"),
            )
            .join(WLMember, WLTeam.team_id == WLMember.team_id, isouter=True)
            .group_by(WLTeam.team_id)
            .all()
        )

        data = [
            {
                "team_id": result.team_id,
                "team_name": result.team_name,
                "member_count": result.member_count,
            }
            for result in results
        ]

        return {"team": data}


class LevelEnum(str, Enum):
    ALL = "All"
    Entry = "Entry"
    Junior = "Junior"
    Senior = "Senior"
    Leader = "Leader"


@work_load_router.get("/member-list", status_code=status.HTTP_200_OK)
async def get_member_list(level: LevelEnum = Query(...)):
    with Session() as session:
        results = (
            session.query(
                WLMember.member_id,
                WLMember.member_name,
                WLMember.member_photo,
                WLMember.member_email,
                WLMember.team_id,
                func.coalesce(WLTeam.team_name, "Undefined").label("team_name"),
                WLMember.member_level,
            )
            .outerjoin(WLTeam, WLMember.team_id == WLTeam.team_id)
            .order_by(WLMember.team_id)
        )

        level_order = {"Entry": 0, "Junior": 1, "Senior": 2, "Leader": 3}

        # by level
        if level == "Leader":
            results = results.filter(WLMember.member_level == "Leader")
        elif level != "All":
            results = results.filter(WLMember.member_level != "Leader")

        data = [
            {
                "member_id": result.member_id,
                "member_name": result.member_name,
                "member_photo": result.member_photo,
                "member_email": result.member_email,
                "team_name": result.team_name,
                "member_level": result.member_level,
                "team_id": result.team_id,
            }
            for result in results
        ]

    return {
        "member_list": sorted(
            data, key=lambda x: level_order[x["member_level"]], reverse=True
        )
    }


# add main project
@work_load_router.post("/add-project", status_code=status.HTTP_201_CREATED)
async def add_main_project(project_info: AddMainProject):
    # SQL
    created_time = int(datetime.now().replace(microsecond=0).timestamp())

    try:
        project_info.project_KPI = int(project_info.project_KPI)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="KPI is not intenger"
        )

    with Session() as session:
        new_main_project = WLMainProject(
            project_name=project_info.project_name,
            project_kpi=project_info.project_KPI,
            project_created_time=created_time,
            project_updated_time=created_time,
            team_id=project_info.team_id,
            project_distinct_col="|".join([i[0] for i in project_info.distinct_inputs]),
        )
        session.add(new_main_project)
        session.flush()

        # add option
        for option in project_info.option_inputs:
            new_option = WLOption_Answer(
                project_id=new_main_project.project_id,
                option_name=option[0],
                option_revise=option[1] == "True",
                option_color=option[2],
            )
            session.add(new_option)

        session.commit()

    return {
        "detail": f"Project_{project_info.project_name} has been added successfully"
    }


# show main project
@work_load_router.get("/project-list", status_code=status.HTTP_200_OK)
async def get_project_list(current_user=Depends(get_current_user)):
    with Session() as session:
        team_id_ = session.query(WLMember.team_id).filter(
            WLMember.member_id == current_user["id"]
        )

        complete_percentage_subquery = (
            session.query(
                WLFile.project_id.label("c_project_id"),
                func.count(WLData.data_id).label("total_row"),
                func.sum(case([(WLData.row_completed == True, 1)], else_=0)).label(
                    "complete_row"
                ),
            )
            .join(WLData, WLFile.file_id == WLData.file_id, isouter=True)
            .group_by(WLFile.project_id)
            .subquery()
        )

        results = (
            session.query(
                WLMainProject.project_id,
                WLMainProject.project_name,
                WLMainProject.project_kpi,
                WLMainProject.project_created_time,
                WLMainProject.project_updated_time,
                WLTeam.team_name,
                WLMember.member_name,
                case([(WLMainProject.team_id.in_(team_id_), False)], else_=True).label(
                    "diabled"
                ),
                complete_percentage_subquery.c.total_row,
                complete_percentage_subquery.c.complete_row,
            )
            .join(WLTeam, WLMainProject.team_id == WLTeam.team_id, isouter=True)
            .join(
                WLMember,
                and_(
                    WLMember.team_id == WLTeam.team_id,
                    WLMember.member_level == "Leader",
                ),
                isouter=True,
            )
            .outerjoin(
                complete_percentage_subquery,
                WLMainProject.project_id == complete_percentage_subquery.c.c_project_id,
            )
            .all()
        )

        data = [
            {
                "project_id": result.project_id,
                "project_name": result.project_name,
                "project_kpi": result.project_kpi,
                "project_created_time": datetime.fromtimestamp(
                    result.project_created_time
                ).strftime("%Y-%m-%d"),
                "project_updated_time": datetime.fromtimestamp(
                    result.project_updated_time
                ).strftime("%Y-%m-%d"),
                "team_name": result.team_name,
                "leader_name": result.member_name,
                "disabled": result.diabled,
                "complete_percentage": (
                    f"{result.complete_row}/{result.total_row}"
                    if result.total_row
                    else "No record"
                ),
            }
            for result in results
        ]

        return {"project_list": data}


@work_load_router.get("/project-detail", status_code=status.HTTP_200_OK)
async def get_project_detail(project_id: str = Query(...)):
    with Session() as session:
        results = (
            session.query(
                WLFile.file_id,
                WLFile.file_name,
                WLFile.file_size,
                WLFile.file_created_time,
                WLFile.project_id,
                WLFile.file_type,
                WLFile.file_extension,
                WLFile.file_status,
                WLFile.file_priority,
            )
            .filter(WLFile.project_id == int(project_id))
            .all()
        )

        if results is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        data = []
        for result in results:
            size_str = ""
            if result.file_size > 1024 * 1024:
                size_str = f"{int(result.file_size/(1024*1024))} GB"
            elif result.file_size > 1024:
                size_str = f"{int(result.file_size/(1024))} MB"
            else:
                size_str = f"{int(result.file_size)} KB"

            new_result = {
                "project_id": result.project_id,
                "file_id": result.file_id,
                "file_name": result.file_name,
                "file_created_time": datetime.fromtimestamp(
                    result.file_created_time
                ).strftime("%Y-%m-%d"),
                "file_size": size_str,
                "file_type": result.file_type,
                "file_extension": result.file_extension,
                "file_status": result.file_status,
                "file_priority": result.file_priority,
            }
            data.append(new_result)

        return {"project_detail": data}


@work_load_router.post("/upload-task-file", status_code=status.HTTP_201_CREATED)
async def upload_task_file(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    project_id: int = Query(...),
):
    for file in files:
        background_tasks.add_task(process_file, file, project_id, Session)

    return {"detail": "File added successfully"}


# by file:file_data = Column(LargeBinary), deprecated
@work_load_router.get("/download-task-file/{file_id}")
async def download_task_file(file_id: int):
    with Session() as session:
        results = session.query(WLFile).filter(WLFile.file_id == file_id).first()

        file_like = io.BytesIO(results.file_data)
        response = StreamingResponse(file_like, media_type="application/octet-stream")
        response.headers[
            "Content-Disposition"
        ] = f"attachment; filename*=UTF-8''{quote(results.file_name)}"

    return response


@work_load_router.post("/add-team", status_code=status.HTTP_201_CREATED)
async def add_team(team_info: AddTeam):
    with Session() as session:
        leader_member_list = team_info.member_list.copy()
        leader_member_list.append(team_info.manager)

        new_team = WLTeam(team_name=team_info.team_name)
        session.add(new_team)
        session.flush()

        leader_member_update = (
            session.query(WLMember)
            .filter(WLMember.member_id.in_(leader_member_list))
            .all()
        )

        for member in leader_member_update:
            member.team_id = new_team.team_id

        session.commit()

    return {
        "detail": f"Team_{team_info.team_name} added and members updated successfully!"
    }


@work_load_router.post("/upload-task-file-xlsx", status_code=status.HTTP_201_CREATED)
def upload_task_file_xlsx(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    project_id: int = Query(...),
):
    # check xlsx or not
    allowed_types = [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/csv",
    ]

    # check the project has been uoloaded or not
    first_upload = False
    with Session() as session:
        upload_history = (
            session.query(WLMainProject.project_file_format)
            .filter(WLMainProject.project_id == project_id)
            .first()
        )
        if upload_history is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )
        elif upload_history and upload_history.project_file_format is None:
            first_upload = True

    for file in files:
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File type error"
            )
        else:
            background_tasks.add_task(
                process_file_excel, file, project_id, Session, first_upload
            )
            first_upload = False


@work_load_router.get(
    "/download-task-file-xlsx/{file_id}/{answer_or_not}",
    status_code=status.HTTP_200_OK,
)
async def download_task_file_xlsx(file_id: int, answer_or_not: bool):
    with Session() as session:
        # get file info
        result_file = (
            session.query(WLFile.file_name, WLFile.project_id)
            .filter(WLFile.file_id == file_id)
            .first()
        )
        # get format
        result_format = (
            session.query(WLMainProject.project_file_format)
            .filter(WLMainProject.project_id == result_file.project_id)
            .first()
        )

        result_data = (
            session.query(
                WLData.row_data, WLOption_Answer.option_name.label("option_name")
            )
            .filter(WLData.file_id == file_id)
            .join(
                WLOption_Answer,
                WLData.row_complete == WLOption_Answer.option_id,
                isouter=True,
            )
            .order_by(WLData.row_id)
            .all()
        )

        if answer_or_not:
            data = [i.row_data.split("|") + [i.option_name] for i in result_data]
            df = pd.DataFrame(
                data,
                columns=result_format.project_file_format.split("|") + ["complete"],
            )
        else:
            data = [i.row_data.split("|") for i in result_data]
            df = pd.DataFrame(
                data, columns=result_format.project_file_format.split("|")
            )

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        xlsx_data = output.getvalue()

        # header: ASCII, filename: UTF-8
        filename_ascii = result_file.file_name.encode(
            "ascii", errors="replace"
        ).decode()
        filename_utf8 = urllib.parse.quote(result_file.file_name.encode("utf-8"))
        content_disposition = (
            f"attachment; filename*=UTF-8''{filename_utf8}; filename={filename_ascii}"
        )

        return StreamingResponse(
            io.BytesIO(xlsx_data),
            media_type="application/octet-stream",
            headers={"Content-Disposition": content_disposition},
        )


@work_load_router.put("/ask-task", status_code=status.HTTP_201_CREATED)
async def ask_task(project_id: int, current_user=Depends(get_current_user)):
    with Session() as session:
        # TODO
        """
        1. check this agent is in this project or not
        2. whether this agent has achieved the KPI of the project
        """
        # check whether this agent has achieve the cap of this project6

        start_date = int(
            datetime.now()
            .replace(hour=0, minute=0, second=0, microsecond=0)
            .timestamp()
        )
        end_date = int(
            datetime.now()
            .replace(hour=23, minute=59, second=59, microsecond=59)
            .timestamp()
        )
        result_log = (
            session.query(WLLog)
            .filter(
                and_(
                    WLLog.memober_id == current_user["id"],
                    WLLog.project_id == project_id,
                    WLLog.log_type == 2,
                    WLLog.log_time.between(start_date, end_date),
                )
            )
            .all()
        )

        cap = (
            session.query(WLMainProject.project_kpi)
            .filter(WLMainProject.project_id == project_id)
            .first()
        )
        if len(result_log) >= cap.project_kpi:
            return {"detail": "You have reached the cap of this project"}

        # get file format
        result_format = (
            session.query(WLMainProject.project_file_format)
            .filter(WLMainProject.project_id == project_id)
            .first()
        )[0].split("|")

        # get option
        result_options = (
            session.query(WLOption_Answer)
            .filter(WLOption_Answer.project_id == project_id)
            .all()
        )
        Options = [
            {
                "option_id": result.option_id,
                "option_name": result.option_name,
                "option_revise": result.option_revise,
                "option_color": result.option_color,
            }
            for result in result_options
        ]

        # get file id
        result_file_id = (
            session.query(WLFile.file_id)
            .filter(
                and_(
                    WLFile.project_id == project_id,
                    WLFile.file_finish.is_(False),
                    WLFile.file_status == 1,
                )
            )
            .all()
        )
        if result_file_id is None:
            return {"detail": "No task"}

        result_file_id = [i[0] for i in result_file_id]
        print(f"file_id: {result_file_id}")

        # get remain task
        result_remain_task = (
            session.query(WLData)
            .filter(
                and_(
                    WLData.row_member_id == current_user["id"],
                    WLData.file_id.in_(result_file_id),
                    WLData.row_completed.is_(False),
                )
            )
            .order_by(WLData.data_id)
            .all()
        )
        # there are remain tasks

        if not result_remain_task:
            first_10_ids_tuples = (
                session.query(WLData.data_id)
                .filter(
                    and_(
                        WLData.file_id.in_(result_file_id),
                        WLData.row_member_id.is_(None),
                    )
                )
                .order_by(WLData.data_id)
                .limit(10)
                .all()
            )

            first_10_ids = [i[0] for i in first_10_ids_tuples]
            session.query(WLData).filter(WLData.data_id.in_(first_10_ids)).update(
                {WLData.row_member_id: current_user["id"]},
                synchronize_session="fetch",
            )

            session.commit()

            result_remain_task = (
                session.query(WLData)
                .filter(WLData.data_id.in_(first_10_ids))
                .order_by(WLData.data_id)
                .all()
            )

        task_items = []
        for i in result_remain_task:
            task_item = dict(zip(result_format, i.row_data.split("|")))
            task_item["id"] = i.data_id
            task_item["disabled"] = False
            task_items.append(task_item)

        return {
            "taskFormat": result_format,
            "task": task_items,
            "option": Options,
        }


@work_load_router.post("/submit-task-list")
async def submit_task(
    files: List[SubmitTask],
):
    file_ids = [file.file_id for file in files if file.file_status == 1]

    with Session() as session:
        for file in files:
            session.query(WLFile).filter(WLFile.file_id == file.file_id).update(
                {
                    WLFile.file_priority: file.file_priority,
                    WLFile.file_status: file.file_status,
                },
                synchronize_session="fetch",
            )

        wl_data_alias = aliased(WLData)
        partition_by_condition = wl_data_alias.row_distinct_detemine

        # Step 1: 创建一个子查询，获取所有 row_num > 1 的 id
        duplicate_ids_subquery = (
            session.query(
                wl_data_alias.data_id.label("duplicate_id"),
                func.row_number()
                .over(
                    partition_by=partition_by_condition, order_by=wl_data_alias.data_id
                )
                .label("row_num"),
            )
            .filter(
                wl_data_alias.file_id.in_(file_ids),
            )
            .subquery()
        )

        duplicate_ids = [
            row.duplicate_id
            for row in session.query(duplicate_ids_subquery)
            .filter(duplicate_ids_subquery.c.row_num > 1)
            .all()
        ]

        (
            session.query(WLData)
            .filter(
                and_(WLData.data_id.in_(duplicate_ids), WLData.row_completed.is_(False))
            )
            .update({WLData.row_member_id: -1}, synchronize_session="fetch")
        )
        (
            session.query(WLData)
            .filter(
                and_(
                    ~WLData.data_id.in_(duplicate_ids), WLData.row_completed.is_(False)
                )
            )
            .update({WLData.row_member_id: None}, synchronize_session="fetch")
        )
        session.commit()
    return {"message": "success"}


@work_load_router.post("/submit-answer")
async def submit_answer(
    submit_info: SubmitRequest, current_user=Depends(get_current_user)
):
    now = int(datetime.now().replace(microsecond=0).timestamp())

    with Session() as session:
        # print(f"submit_info: {(submit_info.project_id)}")

        for ans in submit_info.answers:
            # find answer's name

            subquery = (
                session.query(WLData.row_distinct_detemine)
                .filter(WLData.data_id == ans.data_id)
                .subquery()
            )

            option_revise = (
                session.query(WLOption_Answer.option_revise)
                .filter(WLOption_Answer.option_id == ans.option_id)
                .first()
            )

            update_values = {
                "row_complete": ans.option_id,
                "row_customed": ans.customer_answer,
                "row_completed": True,
                "row_modify_time": now,
            }
            # if option_revise.option_revise is True, we need to keep duplicate data's member_id = -1
            if option_revise.option_revise is False:
                update_values["row_member_id"] = current_user["id"]

            session.query(WLData).filter(
                WLData.row_distinct_detemine == subquery
            ).update(
                update_values,
                synchronize_session="fetch",
            )

            optiopn_type = (
                session.query(WLOption_Answer.option_revise)
                .filter(WLOption_Answer.option_id == ans.option_id)
                .first()
            )
            new_log = WLLog(
                log_time=now,
                project_id=submit_info.project_id,
                data_id=ans.data_id,
                memober_id=current_user["id"],
                log_type=2 if optiopn_type.option_revise is False else 3,
            )
            session.add(new_log)

        session.commit()

    return {"message": "success"}


# TODO: disabled feature: check who can edit the task, only the assignee and mangager can edit the task


@work_load_router.put("/onhold-task", status_code=status.HTTP_201_CREATED)
async def onhold_task(project_id: int, current_user=Depends(get_current_user)):
    print(current_user)

    with Session() as session:
        file_ = (
            session.query(
                WLFile.file_id,
            )
            .filter(WLFile.project_id == project_id)
            .all()
        )
        print("go")
        file_ids = [file.file_id for file in file_]
        print(file_ids)
        results = (
            session.query(
                WLData.data_id,
                WLData.row_data,
                WLMember.member_id,
                WLMember.member_name,
                WLOption_Answer.option_name,
                WLOption_Answer.option_revise,
            )
            .join(WLOption_Answer, WLData.row_complete == WLOption_Answer.option_id)
            .join(WLMember, WLData.row_member_id == WLMember.member_id)
            .filter(
                and_(
                    WLOption_Answer.option_revise.is_(True),
                    WLData.row_member_id != -1,
                    WLOption_Answer.option_name != "",
                    WLData.file_id.in_(file_ids),
                )
            )
            .limit(10)
        )

        result_format = (
            session.query(WLMainProject.project_file_format)
            .filter(WLMainProject.project_id == project_id)
            .first()
        )
        result_format = result_format[0].split("|")

        task_items = []
        for i in results:
            item = i.row_data.split("|")
            task_item = dict(zip(result_format, item))
            task_item["id"] = i.data_id
            task_item["option_name"] = i.option_name
            task_item["editor"] = i.member_name
            task_item["disabled"] = (
                i.member_id != current_user["id"] and current_user["level"] != "Leader"
            )

            task_items.append(task_item)

        # return outcome

        result_options = (
            session.query(WLOption_Answer)
            .filter(
                and_(WLOption_Answer.project_id == project_id),
                WLOption_Answer.option_revise.is_(False),
            )
            .all()
        )
        Options = []
        for result in result_options:
            option = {
                "option_id": result.option_id,
                "option_name": result.option_name,
                "option_revise": result.option_revise,
                "option_color": result.option_color,
            }

            Options.append(option)
        print(Options)

    return {"taskFormat": result_format, "task": task_items, "option": Options}


@work_load_router.post("/record-KPI", status_code=status.HTTP_201_CREATED)
async def record_KPI(submit_info: SubmitKPI, current_user=Depends(get_current_user)):
    now = int(datetime.now().replace(microsecond=0).timestamp())

    with Session() as session:
        new_KPI = WLKPI(
            member_id=current_user["id"],
            KPI_start_time=int(submit_info.KPI_start_time.timestamp()),
            KPI_end_time=int(submit_info.KPI_end_time.timestamp()),
            KPI_content=submit_info.KPI_content,
            KPI_amount=submit_info.KPI_amount,
            KPI_record_time=now,
        )
        session.add(new_KPI)
        session.commit()


@work_load_router.get(
    "/get-KPI/{start_time}/{end_time}", status_code=status.HTTP_200_OK
)
async def get_KPI(
    start_time: datetime, end_time: datetime, current_user=Depends(get_current_user)
):
    print(f"時間點：{start_time} ~ {end_time}")
    start_time, end_time = int(start_time.timestamp()), int(end_time.timestamp())

    with Session() as session:
        KPI_results = (
            session.query(
                WLKPI.KPI_start_time,
                WLKPI.KPI_end_time,
                WLKPI.KPI_content,
                WLKPI.KPI_amount,
                WLKPI.KPI_record_time,
                WLKPI.member_id,
                WLMember.member_name,
            )
            .join(WLMember, WLKPI.member_id == WLMember.member_id)
            .filter(
                or_(
                    WLKPI.KPI_start_time.between(start_time, end_time),
                    WLKPI.KPI_end_time.between(start_time, end_time),
                ),
            )
        ).all()

        KPI = [
            {
                "KPI_start_time": datetime.fromtimestamp(
                    result.KPI_start_time
                ).strftime("%Y-%m-%d %H:%M:%S"),
                "KPI_end_time": datetime.fromtimestamp(result.KPI_end_time).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "KPI_content": result.KPI_content,
                "KPI_amount": result.KPI_amount,
                "KPI_record_time": datetime.fromtimestamp(
                    result.KPI_record_time
                ).strftime("%Y-%m-%d"),
                "KPI_percetage": "{:.0f}%".format(
                    abs(result.KPI_end_time - result.KPI_start_time) / (8 * 3600) * 100
                ),
                "member_name": result.member_name,
                "disable": (
                    current_user["level"] != "Leader"
                    and current_user["id"] != result.member_id
                ),
            }
            for result in KPI_results
        ]
        log_reults = session.query(WLLog).filter(
            and_(
                WLLog.memober_id == current_user["id"],
                WLLog.log_time.between(start_time, end_time),
            )
        )
        log = [
            {
                "log_time": datetime.fromtimestamp(result.log_time).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "project_id": result.project_id,
                "data_id": result.data_id,
                "log_type": "提交" if result.log_type == 2 else "暫緩",
            }
            for result in log_reults
        ]

    return {"KPI": KPI, "log": log}
