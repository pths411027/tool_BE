import os
from datetime import datetime
from fastapi import FastAPI, APIRouter, UploadFile, Form, File, Request, HTTPException
from app.database.sqlalchemy import Session, engine
import json
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()

data_suite_router = APIRouter(tags=["Data Suite"], prefix="/data-suite")


@data_suite_router.get("/home")
async def data_suite_home():
    return {"data_suite_router": "home"}


    
from app.routers.data_suite.request_model import Query_info


import sqlparse
from app.routers.data_suite.utils import get_db

@data_suite_router.post("/query")
async def data_suite_query(query_info: Query_info):
    print(query_info)
    column_names, data = get_db(query_info.query, Session, 10)  
    if column_names == 400:
        raise HTTPException(status_code=400, detail=data)
    else:
        return {"column_names": list(column_names),  "data": data[:5]}


from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse

import io
import pandas as pd

@data_suite_router.post("/download")
async def data_suite_download(query_info: Query_info):
    column_names, data = get_db(query_info.query, Session, -1)
    if column_names == 400:
        raise HTTPException(status_code=400, detail=data)
    else:
        df = pd.DataFrame(data)
        
    
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=query_output.csv"
    response.headers["output-filename"] = "=query_output.csv"
    return response




from sqlalchemy import MetaData
from app.database.sqlalchemy import Base
@data_suite_router.get("/table")
async def data_suite_table():
    table_list = list(Base.metadata.tables.keys())
    return {'table_list':table_list}


import pygsheets
@data_suite_router.get("/google-sheet-name")
async def data_suite_google_sheet_name(url: str):
    gc = pygsheets.authorize(service_account_file = "app/Credentials.json")
    try:
        worksheets = gc.open_by_url(url).worksheets()
        sheet_list = [ws.title for ws in worksheets]  # 获取工作表名字列表
        print('Good')
        return {'status':'success',
                'sheet_list': sheet_list}
    except:
        print('Not Good')
        return {'status':'fail'}
        # raise HTTPException(status_code=400, detail="Invalid url")


from fastapi import BackgroundTasks
from app.routers.data_suite.utils import write_to_google_sheet
from app.routers.data_suite.request_model import Google_sheet
@data_suite_router.post("/google-sheet")
async def data_suite_google_sheet(Google_sheet_info: Google_sheet,
                                  background_tasks: BackgroundTasks,  # add this parameter
                                  ):
    print(Google_sheet_info)
    column_names, data = get_db(Google_sheet_info.query, Session, -1)
    df = pd.DataFrame(data)
    

    gc = pygsheets.authorize(service_account_file="app/Credentials.json")
    wb = gc.open_by_url(Google_sheet_info.url)
    sheet = wb.worksheet_by_title(Google_sheet_info.sheet_name)

    # Add task to background
    
    background_tasks.add_task(write_to_google_sheet, df, sheet, Google_sheet_info.start_cell, Google_sheet_info.include_header)
    return {"message": "Data written to Google Sheet successfully"}

from app.routers.data_suite.request_model import Google_sheet_task
from app.schemas.DS import DataSuiteTask
@data_suite_router.post("/google-sheet-task")
async def data_suite_google_sheet_task(Google_sheet_task_info: Google_sheet_task):
    print(Google_sheet_task_info)
    
    with Session() as session:
        new_task = DataSuiteTask(
            task_name = Google_sheet_task_info.task_name,
            task_url = Google_sheet_task_info.url,
            task_sheet_name = Google_sheet_task_info.sheet_name,
            task_start_cell = Google_sheet_task_info.start_cell,
            task_include_header = Google_sheet_task_info.include_header,
            task_query = Google_sheet_task_info.query,
            task_frequency = Google_sheet_task_info.frequency,
            run_time = Google_sheet_task_info.run_time
        )
        session.add(new_task)
        session.commit()

    return None    

# airflow will trigger this api
from sqlalchemy import extract

@data_suite_router.get("/run-google-sheet-task")
async def data_suite_run_google_sheet_task():
    # now 現在幾點
    now = int(datetime.now().strftime("%H"))
    print(now)
    print(type(now))
    
    with Session() as session:
        # daily
        run_task_daily = session.query(DataSuiteTask
                                        ).filter(extract('hour', DataSuiteTask.run_time) == int(now)
                                        ).filter(DataSuiteTask.task_frequency == 'daily'
                                            ).all()
        if run_task_daily is not None:
            for task in run_task_daily:
                column_names, data = get_db(task.task_query, Session, -1)
                df = pd.DataFrame(data)

                gc = pygsheets.authorize(service_account_file="app/Credentials.json")
                wb = gc.open_by_url(task.task_url)
                sheet = wb.worksheet_by_title(task.task_sheet_name)
                write_to_google_sheet(df, sheet, task.task_start_cell, task.task_include_header)

        # hourly
        run_task_hourly = session.query(DataSuiteTask
                                        ).filter(DataSuiteTask.task_frequency == 'hourly'
                                            ).all()
        if run_task_hourly is not None:
            for task in run_task_hourly:
                column_names, data = get_db(task.task_query, Session, -1)
                df = pd.DataFrame(data)

                gc = pygsheets.authorize(service_account_file="app/Credentials.json")
                wb = gc.open_by_url(task.task_url)
                sheet = wb.worksheet_by_title(task.task_sheet_name)
                write_to_google_sheet(df, sheet, task.task_start_cell, task.task_include_header)
        