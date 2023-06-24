import os
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, APIRouter, UploadFile, Form, File, Request, HTTPException, Path, Query
from typing import List
from app.database.sqlalchemy import Session, engine
import json
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()


work_load_router = APIRouter(tags=["Work Load"], prefix="/work_load")


@work_load_router.get("/home")
async def pm_server_home():
    return {"work_load_router": "home"}


from .request_model import AddTeam
from app.schemas.WL import WLTeam

# add team
@work_load_router.post("/add_team")
async def add_team(team_info:AddTeam):
    print(team_info)
    with Session() as session:
        existing_team = session.query(WLTeam).filter_by(teamName=team_info.teamName).first()
        if existing_team:
            raise HTTPException(status_code=400, detail="Team already exists")
        new_team = WLTeam(
            teamName = team_info.teamName
        )
        session.add(new_team)
        session.commit()
    return {"message": "Team added successfully"}


@work_load_router.get("/team-list")
async def get_team_list():
     with Session() as session:
        query = session.query(WLTeam.teamName)
        results = query.all()
        
        data = [
            result.teamName
            for result in results
        ]
       
        print(data)
        # return outcome
        return {"team": data}


# add team
from .request_model import AddMember
from app.schemas.WL import WLMember

@work_load_router.post("/add_member")
async def add_team(member_info:AddMember):
    print(member_info)

    
    with Session() as session:
        
        existing_member = session.query(WLMember).filter_by(memberName=member_info.memberName).first()
        if existing_member:
            raise HTTPException(status_code=400, detail="Member already exists")
        

        new_member = WLMember(
            memberName = member_info.memberName,
            memberPhoto = member_info.memberPhoto,
            email =  member_info.memberEmail + member_info.memberEmailType,
            team_id = 0,
            level = member_info.memberLevel
        )
        session.add(new_member)
        session.commit()
    return {"message": "Team added successfully"}
    

from .request_model import AddMainProject
from app.schemas.WL import WLMainProject

# add main project
@work_load_router.post("/add-project")
async def add_main_project(project_info:AddMainProject):
    print(project_info)
    # SQL
    try:
        project_info.KPI = int(project_info.KPI)
    except:
        raise HTTPException(status_code=400, detail="KPI is not int")

    created_time = datetime.now()
    with Session() as session:
        new_main_project = WLMainProject(
            project_name = project_info.projectName,
            KPI = int(project_info.KPI),
            created_time = created_time,
            updated_time = created_time,
            team = project_info.team
        )
        session.add(new_main_project)
        session.commit()  

    return {"message": "Project added successfully"}
    

# show main project
@work_load_router.get("/project-list")
async def get_project_list():
   
    with Session() as session:
        query = session.query(WLMainProject.project_id,
                              WLMainProject.project_name,
                              WLMainProject.KPI,
                              WLMainProject.created_time,
                              WLMainProject.updated_time,
                              WLMainProject.team)
        results = query.all()
        
        data = [
            {   
                "pro_id": result.project_id,
                "project_name": result.project_name,
                "KPI": result.KPI,
                "created_time": result.created_time.strftime("%Y-%m-%d"),
                "updated_time": result.updated_time.strftime("%Y-%m-%d"),
                "team":result.team
            }
            for result in results
        ]

        # return outcome
        return {"project_list": data}
    
# show project detail by pro_id
from app.schemas.WL import WLFile, WLData
@work_load_router.get("/project-detail")
async def get_project_detail(pro_id: str = Query(...)):
    print(pro_id)
    with Session() as session:
        # 使用 filter_by 在数据库查询中使用 pro_id
        
        results = session.query(WLFile.file_id,
                                WLFile.file_name,
                                WLFile.created_time,
                                WLFile.project_id,
                                    ).filter(WLFile.project_id == int(pro_id)).all()

        # 检查是否找到了对应的项目
        if results is None:
            raise HTTPException(status_code=404, detail="Project not found")
        print('答案')
        print(results)

        # 将结果转换为字典
        data = []
        for result in results:
            item_sum = session.query(WLData.row_id).filter(WLData.file_id == result.file_id).count()

            new_result = {   
                    "project_id": result.project_id,
                    "file_name": result.file_name,
                    "created_time": result.created_time.strftime("%Y-%m-%d"),
                    "item_sum":item_sum,
            }
            data.append(new_result)

        print(data)
        
        return {"project_detail": data}



from .request_model import AddFile
@work_load_router.post("/upload-task-file")
async def upload_task_file(files: List[UploadFile] = File(...), pro_id: int = Query(...)):

    for file in files:
        df = pd.read_excel(file.file)
        created_time = datetime.now().replace(microsecond=0)
        # 寫入資料資訊

        with Session() as session:
            new_file_info = WLFile(
                file_name = file.filename,
                created_time = created_time,
                project_id = pro_id
            )

            session.add(new_file_info)
            session.flush()
                
            for _, row in df.iterrows():
                row_data = "->".join(str(row[column]) for column in df.columns)
                print(row_data)
                wl_data = WLData(
                    file_id = new_file_info.file_id,
                    row_id = row.name,
                    row_data = row_data,
                    row_complete="",
                    row_customed=""
                )
                session.add(wl_data)
            session.commit()
    return {"message": "File added successfully"}