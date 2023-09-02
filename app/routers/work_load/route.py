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
    FastAPI,
    File,
    HTTPException,
    Query,
    UploadFile,
)
from sqlalchemy import and_, func
from sqlalchemy.orm import aliased
from starlette.responses import StreamingResponse

from app.database.sqlalchemy import Session
from app.routers.work_load.BE_tool_func import process_file, process_file_excel
from app.schemas.WL import (
    WLData,
    WLFile,
    WLMainProject,
    WLMember,
    WLOption_Answer,
    WLTeam,
)

# add team
from .request_model import AddMainProject, AddMember, AddTeam, SubmitRequest, SubmitTask

load_dotenv()
app = FastAPI()
work_load_router = APIRouter(tags=["Work Load"], prefix="/work-load")


@work_load_router.get("/home")
async def pm_server_home():
    return {"work_load_router": "home"}


@work_load_router.get("/team-list")
async def get_team_list():
    with Session() as session:
        results = (
            session.query(
                WLTeam.teamName, func.count(WLMember.member_id).label("member_count")
            )
            .join(WLMember, WLTeam.team_id == WLMember.team_id, isouter=True)
            .group_by(WLTeam.teamName)
            .all()
        )

        data = [
            {"teamName": result.teamName, "memberCount": result.member_count}
            for result in results
        ]

        print(data)
        return {"team": data}


@work_load_router.post("/add_member")
async def add_member(member_info: AddMember):
    print(member_info)
    with Session() as session:
        existing_member = (
            session.query(WLMember).filter_by(memberName=member_info.memberName).first()
        )
        if existing_member:
            raise HTTPException(status_code=400, detail="Member already exists")

        if member_info.memberEmailType == "":
            member_info.memberEmailType = "@gmail.com"
            print("add")
        else:
            print(f"now:{member_info.memberEmailType}")

        new_member = WLMember(
            memberName=member_info.memberName,
            memberPhoto=member_info.memberPhoto,
            email=member_info.memberEmail + member_info.memberEmailType,
            team_id=0,
            level=member_info.memberLevel,
        )
        session.add(new_member)
        session.commit()
    return {"message": "Team added successfully"}


class LevelEnum(str, Enum):
    ALL = "All"
    Entry = "Entry"
    Junior = "Junior"
    Senior = "Senior"
    Leader = "Leader"


@work_load_router.get("/member-list")
async def get_member_list(level: LevelEnum = Query(...)):
    data = []
    with Session() as session:
        results = (
            session.query(
                WLMember.member_id,
                WLMember.memberName,
                WLMember.memberPhoto,
                WLMember.email,
                func.coalesce(WLTeam.teamName, "未定").label("teamName"),
                WLMember.level,
            )
            .outerjoin(WLTeam, WLMember.team_id == WLTeam.team_id)
            .order_by(WLMember.team_id)
        )

        level_order = {"Entry": 0, "Junior": 1, "Senior": 2, "Leader": 3}

        # 根據 level 的值修改查詢
        if level != "All":
            if level == "Leader":
                results = results.filter(WLMember.level == "Leader")
            else:
                results = results.filter(WLMember.level != "Leader")

        data = [
            {
                "member_id": result.member_id,
                "memberName": result.memberName,
                "memberPhoto": result.memberPhoto,
                "email": result.email,
                "teamName": result.teamName,
                "level": result.level,
            }
            for result in results
        ]
        data = sorted(data, key=lambda x: level_order[x["level"]], reverse=True)
        print(data)

    return {"member_list": data}


# add main project
@work_load_router.post("/add-project")
async def add_main_project(project_info: AddMainProject):
    print(project_info.optionInputs)

    # SQL
    try:
        project_info.KPI = int(project_info.KPI)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"KPI is not int: {e}")

    created_time = datetime.now()

    with Session() as session:
        team_id = (
            session.query(WLTeam.team_id)
            .filter(WLTeam.teamName == project_info.team)
            .first()
        )
        print(team_id)

        distinct_col = []
        for i in project_info.distinctInputs:
            distinct_col.append(i[0])

        new_main_project = WLMainProject(
            project_name=project_info.projectName,
            KPI=int(project_info.KPI),
            created_time=created_time,
            updated_time=created_time,
            team=team_id.team_id,
            distinct_col="|".join([i[0] for i in project_info.distinctInputs]),
        )
        session.add(new_main_project)
        session.flush()

        # add option
        for option in project_info.optionInputs:
            print(option)
            option[1] = option[1] == "True"

            new_option = WLOption_Answer(
                project_id=new_main_project.project_id,
                option_name=option[0],
                option_revise=option[1],
                option_color=option[2],
            )
            session.add(new_option)

        session.commit()

    return {"message": "Project added successfully"}


# show main project
@work_load_router.get("/project-list")
async def get_project_list():
    with Session() as session:
        query = session.query(
            WLMainProject.project_id,
            WLMainProject.project_name,
            WLMainProject.KPI,
            WLMainProject.created_time,
            WLMainProject.updated_time,
            WLMainProject.team,
        )
        results = query.all()

        data = [
            {
                "pro_id": result.project_id,
                "project_name": result.project_name,
                "KPI": result.KPI,
                "created_time": result.created_time.strftime("%Y-%m-%d"),
                "updated_time": result.updated_time.strftime("%Y-%m-%d"),
                "team": result.team,
            }
            for result in results
        ]

        # return outcome
        return {"project_list": data}


# show project detail by pro_id


@work_load_router.get("/project-detail")
async def get_project_detail(pro_id: str = Query(...)):
    print(pro_id)
    with Session() as session:
        # 使用 filter_by 在数据库查询中使用 pro_id

        results = (
            session.query(
                WLFile.file_id,
                WLFile.file_name,
                WLFile.file_size,
                # WLFile.file_data,
                WLFile.created_time,
                WLFile.project_id,
                WLFile.file_type,
                WLFile.file_extension,
                WLFile.file_status,
                WLFile.file_priority,
            )
            .filter(WLFile.project_id == int(pro_id))
            .all()
        )

        # 检查是否找到了对应的项目
        if results is None:
            raise HTTPException(status_code=404, detail="Project not found")
        print("答案")
        print(results)

        # 将结果转换为字典
        data = []
        for result in results:
            print(f"d:{result.file_size}, {type(result.file_size)}")

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
                "created_time": datetime.fromtimestamp(result.created_time).strftime(
                    "%Y-%m-%d"
                ),
                "file_size": size_str,
                "file_type": result.file_type,
                "file_extension": result.file_extension,
                "file_status": result.file_status,
                "file_priority": result.file_priority,
            }
            data.append(new_result)

        print(data)

        return {"project_detail": data}


# from .request_model import AddFile
@work_load_router.post("/upload-task-file")
async def upload_task_file(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    pro_id: int = Query(...),
):
    for file in files:
        print(file.filename)
        background_tasks.add_task(process_file, file, pro_id, Session)

    return {"message": "File added successfully"}


# by file:file_data = Column(LargeBinary), deprecated
@work_load_router.get("/download-task-file/{file_id}")
async def download_task_file(file_id: int):
    print(f"file_id: {file_id}")
    with Session() as session:
        results = session.query(WLFile).filter(WLFile.file_id == file_id).first()

        file_like = io.BytesIO(results.file_data)
        response = StreamingResponse(file_like, media_type="application/octet-stream")
        response.headers[
            "Content-Disposition"
        ] = f"attachment; filename*=UTF-8''{quote(results.file_name)}"

    return response


@work_load_router.post("/add-team")
async def add_team(team_info: AddTeam):
    try:
        with Session() as session:
            leader_member_list = team_info.memberList.copy()
            leader_member_list.append(team_info.manager)

            new_team = WLTeam(teamName=team_info.teamName)
            session.add(new_team)
            session.flush()

            for id in leader_member_list:
                result = (
                    session.query(WLMember).filter(WLMember.member_id == id).first()
                )
                if result:
                    result.team_id = new_team.team_id

            session.commit()

        return {"message": "Team added and members updated successfully!"}
    except Exception as e:
        print(f"Caught exception: {e}")
        return {"error": str(e)}


@work_load_router.post("/upload-task-file-xlsx")
def upload_task_file_xlsx(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    pro_id: int = Query(...),
):
    # check xlsx or not
    allowed_types = [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/csv",
    ]
    """
    if file.content_type in allowed_types:
        pass
    else:
        raise HTTPException(status_code=400, detail="File type error")
    """
    # check the project has been uoloaded or not
    first_upload = False
    with Session() as session:
        upload_history = (
            session.query(WLMainProject.file_format)
            .filter(WLMainProject.project_id == pro_id)
            .first()
        )
        print(f"upload_history: {upload_history.file_format}.")
        if upload_history.file_format is None:
            print("還沒有上傳過")
            first_upload = True
            pass
        else:
            print("已經上傳過")
            pass

    for file in files:
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="File type error")
        else:
            background_tasks.add_task(
                process_file_excel, file, pro_id, Session, first_upload
            )
            first_upload = False


@work_load_router.get("/download-task-file-xlsx/{file_id}")
async def download_task_file_xlsx(file_id: int):
    with Session() as session:
        # get file info
        result_file = (
            session.query(WLFile.file_name).filter(WLFile.file_id == file_id).first()
        )
        print(result_file)

        # get data
        result_data = session.query(WLData).filter(WLData.file_id == file_id).all()

        data = [i.row_data.split("|") for i in result_data]
        df = pd.DataFrame(data)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, header=False)
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


# TODO
"""
1. 檢查此要求者是否屬於該端案
2. 檢查此要求者是否已經完成當日的份額
3. 檢查有沒有已經要求但還沒繳交的
4. 任務優先級排序
    (1) 原則上，按照時間先後順序
    (2) 提供可以供調整的煙優掂及概念
    (3) ...

"""


@work_load_router.post("/ask-task")
async def ask_task(project_id: int, member_id: int):
    # KYC
    with Session() as session:
        # TODO
        """
        1. check this agent is in this project or not
        2. whether this agent has achieved the KPI of the project
        """
        # get file format
        result_format = (
            session.query(WLMainProject.file_format)
            .filter(WLMainProject.project_id == project_id)
            .first()
        )
        print(f"format:  {result_format}")

        # get option
        result_options = (
            session.query(WLOption_Answer)
            .filter(WLOption_Answer.project_id == project_id)
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
        if result_file_id == None:
            return {"message": "No task"}
        else:
            print("No~~")

        result_file_id = [i[0] for i in result_file_id]
        print(f"file_id: {result_file_id}")

        # get remain task
        result_remain_task = (
            session.query(WLData)
            .filter(
                and_(
                    WLData.member_id == member_id,
                    WLData.file_id.in_(result_file_id),
                    WLData.completed.is_(False),
                )
            )
            .order_by(WLData.id)
            .all()
        )
        if result_remain_task:
            # there are remain tasks
            print("there are remain tasks")
            result_format = result_format[0].split("|")
            task_items = []
            for i in result_remain_task:
                item = i.row_data.split("|")
                task_item = dict(zip(result_format, item))
                task_item["id"] = i.id
                print(task_item)
                task_items.append(task_item)

            return {
                "taskFormat": result_format,
                "task": task_items,
                "option": Options,
            }

        # 查询出前10条数据的ID
        first_10_ids_tuples = (
            session.query(WLData.id)
            .filter(
                and_(
                    WLData.file_id.in_(result_file_id),
                    WLData.member_id.is_(None),
                )
            )
            .limit(10)
            .all()
        )

        first_10_ids = [i[0] for i in first_10_ids_tuples]
        for i in first_10_ids:
            print(i)
            session.query(WLData).filter(WLData.id.in_(first_10_ids)).update(
                {WLData.member_id: member_id}, synchronize_session="fetch"
            )
        session.commit()

        result_data = (
            session.query(WLData)
            .filter(WLData.id.in_(first_10_ids))
            .order_by(WLData.id)
            .all()
        )

        result_format = result_format[0].split("|")
        print(f"format:  {result_format}")
        task_items = []

        for i in result_data:
            item = i.row_data.split("|")
            task_item = dict(zip(result_format, item))
            task_item["id"] = i.id
            print(task_item)
            task_items.append(task_item)
        return {"taskFormat": result_format, "task": task_items, "option": Options}


@work_load_router.post("/submit-task-list")
async def submit_task(
    files: List[SubmitTask],
    pro_id: int = Query(...),
):
    print("start")
    print(files)
    for file in files:
        print(file.file_id)
    print(pro_id)

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
        partition_by_condition = wl_data_alias.distinct_detemine

        # Step 1: 创建一个子查询，获取所有 row_num > 1 的 id
        duplicate_ids_subquery = (
            session.query(
                wl_data_alias.id.label("duplicate_id"),
                func.row_number()
                .over(partition_by=partition_by_condition, order_by=wl_data_alias.id)
                .label("row_num"),
            )
            .filter(wl_data_alias.file_id.in_(file_ids))
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
            .filter(WLData.id.in_(duplicate_ids))
            .update({WLData.member_id: -1}, synchronize_session="fetch")
        )
        (
            session.query(WLData)
            .filter(~WLData.id.in_(duplicate_ids))
            .update({WLData.member_id: None}, synchronize_session="fetch")
        )
        session.commit()
    return {"message": "success"}


@work_load_router.post("/submit-answer")
async def submit_answer(submit_info: SubmitRequest):
    # print(submit_info.member_id)
    now = int(datetime.now().replace(microsecond=0).timestamp())

    with Session() as session:
        for ans in submit_info.answers:
            print(f"{ans.id}: {ans.option_id}_{ans.customer_answer}")

            # find answer's name
            ans_name = (
                session.query(WLOption_Answer.option_name)
                .filter(WLOption_Answer.option_id == ans.option_id)
                .first()
            )
            print(ans_name.option_name)

            subquery = (
                session.query(WLData.distinct_detemine)
                .filter(WLData.id == ans.id)
                .subquery()
            )
            session.query(WLData).filter(WLData.distinct_detemine == subquery).update(
                {
                    "row_complete": ans_name.option_name,
                    "row_customed": ans.customer_answer,
                    "completed": True,
                    "modify_time": now,
                    "member_id": submit_info.member_id,
                },
                synchronize_session="fetch",
            )
            result = (
                session.query(WLData.distinct_detemine)
                .filter(WLData.id == ans.id)
                .first()
            )
            A = (
                session.query(WLData)
                .filter(WLData.distinct_detemine == result.distinct_detemine)
                .all()
            )
            for a in A:
                print(a.id)

        session.commit()

    print(submit_info.answers)
    return {"message": "success"}
