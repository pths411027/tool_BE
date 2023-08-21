import json
import os
from datetime import datetime
from typing import List

import pandas as pd
from dotenv import load_dotenv
from fastapi import (
    APIRouter,
    FastAPI,
    File,
    Form,
    HTTPException,
    Path,
    Query,
    Request,
    UploadFile,
)
from sqlalchemy import desc, func

from app.database.sqlalchemy import Session, engine

load_dotenv()
app = FastAPI()
work_load_router = APIRouter(tags=["Work Load"], prefix="/work-load")


@work_load_router.get("/home")
async def pm_server_home():
    return {"work_load_router": "home"}


from app.schemas.WL import WLMember, WLTeam

from .request_model import AddTeam


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


from app.schemas.WL import WLMember

# add team
from .request_model import AddMember


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


from enum import Enum


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


from app.schemas.WL import WLMainProject

from .request_model import AddMainProject


# add main project
@work_load_router.post("/add-project")
async def add_main_project(project_info: AddMainProject):
    print(project_info)
    # SQL
    try:
        project_info.KPI = int(project_info.KPI)
    except:
        raise HTTPException(status_code=400, detail="KPI is not int")

    created_time = datetime.now()
    with Session() as session:
        team_id = (
            session.query(WLTeam.team_id)
            .filter(WLTeam.teamName == project_info.team)
            .first()
        )
        print(team_id)

        new_main_project = WLMainProject(
            project_name=project_info.projectName,
            KPI=int(project_info.KPI),
            created_time=created_time,
            updated_time=created_time,
            team=team_id.team_id,
        )
        session.add(new_main_project)
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
from sqlalchemy import func

from app.schemas.WL import WLData, WLFile


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
                WLFile.file_data,
                WLFile.created_time,
                WLFile.project_id,
                WLFile.file_type,
                WLFile.file_extension,
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
                "created_time": result.created_time.strftime("%Y-%m-%d"),
                "file_size": size_str,
                "file_type": result.file_type,
                "file_extension": result.file_extension,
            }
            data.append(new_result)

        print(data)

        return {"project_detail": data}


import magic
from fastapi import BackgroundTasks

from app.routers.work_load.BE_tool_func import process_file


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


import io
from io import BytesIO
from tempfile import NamedTemporaryFile
from urllib.parse import quote

from starlette.responses import FileResponse, StreamingResponse


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


from app.schemas.WL import WLTeam

from .request_model import AddTeam


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
