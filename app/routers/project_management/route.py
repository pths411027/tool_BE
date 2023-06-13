from datetime import datetime
from fastapi import APIRouter, UploadFile, Form, File, Request
from app.database.sqlite import Session, engine


pm_server_router = APIRouter(tags=["PM Server"], prefix="/pm-server")


@pm_server_router.get("/home")
async def pm_server_home():
    return {"pm_server_router": "home"}

from .request_model import AddMainProject
from app.schemas.PM import MainProject, SubProject

# add main project
@pm_server_router.post("/main-project")
async def add_main_project(project_info:AddMainProject):
    with Session() as session:
        new_main_project = MainProject(
            project_name = project_info.projectName,
            KYC = project_info.KYC,
            des = project_info.description,
            start_day = datetime.strptime(project_info.startDay, "%Y-%m-%d").date(),
            end_day = datetime.strptime(project_info.endDay, "%Y-%m-%d").date(),
            tag = project_info.tag
        )
        session.add(new_main_project)
        session.flush()  

        # 创建 sub_project 对象
        for i in project_info.extraInputs:
            new_sub_project = SubProject(
                parent_pro_id = new_main_project.pro_id,
                project_name = i[0],
                des = i[1],
                tag = i[2]
            )
            session.add(new_sub_project)
        session.commit()
    return {"message": "Project added successfully"}



# show main project
@pm_server_router.get("/now-main-project")
async def get_main_project_columns():
    color_dict = dict()
    color_dict['CICD'] = 'rgba(30, 123, 162, 0.8)'
    color_dict['FE'] = 'rgba(250, 197, 93, 0.8)'
    color_dict['BE'] = 'rgba(237, 106, 95, 0.8)'
    color_dict['PM'] = 'rgba(169, 209, 142, 0.8)'


    with Session() as session:
        query = session.query(MainProject.project_name, MainProject.start_day, MainProject.end_day, MainProject.des, MainProject.tag)
        results = query.all()
        
        data = [
            {
                "project_name": result.project_name,
                "start_day": result.start_day.strftime("%Y-%m-%d"),
                "end_day": result.end_day.strftime("%Y-%m-%d"),
                "description":result.des,
                "tag": result.tag,
                "color":color_dict[result.tag]
            }
            for result in results
        ]

        # 返回结果
        return {"main_projects": data}
        

    
   