import ast
import json
import os
from datetime import datetime

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI

from app.database.sqlalchemy import Session
from app.routers.project_management.BE_tool_func import Send
from app.schemas.PM import MainProject, Member, SubProject

from .request_model import AddMainProject, AddMember

load_dotenv()

app = FastAPI()


pm_server_router = APIRouter(tags=["PM Server"], prefix="/pm-server")


@pm_server_router.get("/home")
async def pm_server_home():
    return {"pm_server_router": "home"}


# add main project
@pm_server_router.post("/add-project")
async def add_main_project(project_info: AddMainProject):
    # SQL
    with Session() as session:
        new_main_project = MainProject(
            project_name=project_info.projectName,
            KYC=project_info.KYC,
            des=project_info.description,
            start_day=datetime.strptime(project_info.startDay, "%Y-%m-%d").date(),
            end_day=datetime.strptime(project_info.endDay, "%Y-%m-%d").date(),
            tag=project_info.tag,
        )
        session.add(new_main_project)
        session.flush()

        # build sub_project object
        for i in project_info.extraInputs:
            new_sub_project = SubProject(
                parent_pro_id=new_main_project.pro_id,
                project_name=i[0],
                des=i[1],
                tag=i[2],
            )
            session.add(new_sub_project)
        session.commit()
    # email
    Send(
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        username=os.environ.get("MARCUS_EMAIL_ACCOUT"),
        password=os.environ.get("MARCUS_EMAIL_PASSWORD"),
        subject="任務通知",
        body=f"{project_info.KYC} 接到新任務：{project_info.projectName}",
        email_to=["marcus.tsai@shopee.com"],
    )

    return {"message": "Project added successfully"}


# show main project
@pm_server_router.get("/main-project")
async def get_main_project_columns():
    color_dict = dict()
    color_dict["CICD"] = "rgba(30, 123, 162, 0.8)"
    color_dict["FE"] = "rgba(250, 197, 93, 0.8)"
    color_dict["BE"] = "rgba(237, 106, 95, 0.8)"
    color_dict["PM"] = "rgba(169, 209, 142, 0.8)"

    with Session() as session:
        query = session.query(
            MainProject.project_name,
            MainProject.start_day,
            MainProject.end_day,
            MainProject.des,
            MainProject.tag,
        )
        results = query.all()

        data = [
            {
                "project_name": result.project_name,
                "start_day": result.start_day.strftime("%Y-%m-%d"),
                "end_day": result.end_day.strftime("%Y-%m-%d"),
                "description": result.des,
                "tag": result.tag,
                "color": color_dict[result.tag],
            }
            for result in results
        ]

        # return outcome
        return {"main_projects": data}


# add member
@pm_server_router.post("/add-member")
async def add_main_member(member_info: AddMember):
    with Session() as session:
        new_member = Member(
            chineseName=member_info.chineseName,
            englishName=member_info.englishName,
            email=member_info.email,
            department=member_info.department,
            team=member_info.team,
            level=member_info.level,
            manager=json.dumps(member_info.manager),
        )
        session.add(new_member)
        session.commit()
    return {"message": "Member added successfully"}


# show member


@pm_server_router.get("/member")
async def get_member():
    with Session() as session:
        query = session.query(
            Member.chineseName,
            Member.englishName,
            Member.department,
            Member.team,
            Member.manager,
            Member.level,
        )
        results = query.all()

        data = [
            {
                "chineseName": result.chineseName,
                "englishName": result.englishName,
                "department": result.department,
                "team": result.team,
                "manager": ast.literal_eval(result.manager),
                "level": result.level,
            }
            for result in results
        ]

        # return outcome
        return {"member": data}


# show memberList
@pm_server_router.get("/member-list")
async def get_member_list():
    with Session() as session:
        query = session.query(Member.englishName).distinct()
        results = query.all()

        data = [result.englishName for result in results]

        # return outcome
        return {"member": data}
