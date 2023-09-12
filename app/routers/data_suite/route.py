import io
from datetime import datetime

import pandas as pd
import pygsheets
from dotenv import load_dotenv
from fastapi import APIRouter, BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import extract

from app.database.sqlalchemy import Base, Session
from app.routers.data_suite.request_model import (Google_sheet,
                                                  Google_sheet_task,
                                                  Query_info, WorkFlow)
from app.routers.data_suite.utils import (get_db, next_runtime_calculator,
                                          unix_time_transformer,
                                          write_to_google_sheet)
from app.schemas.DS import DataSuiteTask, DataSuiteWorkFlow

load_dotenv()

app = FastAPI()

data_suite_router = APIRouter(tags=["Data Suite"], prefix="/data-suite")


@data_suite_router.get("/home")
async def data_suite_home():
    return {"data_suite_router": "home"}


@data_suite_router.post("/query")
async def data_suite_query(query_info: Query_info):
    print(query_info)
    column_names, data = get_db(query_info.query, Session, 10)
    print(column_names)
    print(data)
    if column_names == 400:
        raise HTTPException(status_code=400, detail=data)
    else:
        return {"column_names": list(column_names), "data": data}


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


@data_suite_router.get("/table")
async def data_suite_table():
    table_list = list(Base.metadata.tables.keys())
    return {"table_list": table_list}


@data_suite_router.get("/google-sheet-name")
async def data_suite_google_sheet_name(url: str):
    gc = pygsheets.authorize(service_account_file="app/Credentials.json")
    try:
        worksheets = gc.open_by_url(url).worksheets()
        sheet_list = [ws.title for ws in worksheets]  # 获取工作表名字列表
        print("Good")
        return {"status": "success", "sheet_list": sheet_list}
    except Exception as e:
        print(f"Not Good: {e}")
        return {"status": "fail"}
        # raise HTTPException(status_code=400, detail="Invalid url")


@data_suite_router.post("/google-sheet")
async def data_suite_google_sheet(
    Google_sheet_info: Google_sheet,
    background_tasks: BackgroundTasks,  # add this parameter
):
    print(Google_sheet_info)
    column_names, data = get_db(Google_sheet_info.query, Session, -1)
    df = pd.DataFrame(data)

    gc = pygsheets.authorize(service_account_file="app/Credentials.json")
    wb = gc.open_by_url(Google_sheet_info.url)
    sheet = wb.worksheet_by_title(Google_sheet_info.sheet_name)

    # Add task to background

    background_tasks.add_task(
        write_to_google_sheet,
        df,
        sheet,
        Google_sheet_info.start_cell,
        Google_sheet_info.include_header,
    )
    return {"message": "Data written to Google Sheet successfully"}


@data_suite_router.post("/google-sheet-task")
async def data_suite_google_sheet_task(Google_sheet_task_info: Google_sheet_task):
    print(Google_sheet_task_info)

    with Session() as session:
        new_task = DataSuiteTask(
            task_name=Google_sheet_task_info.task_name,
            task_url=Google_sheet_task_info.url,
            task_sheet_name=Google_sheet_task_info.sheet_name,
            task_start_cell=Google_sheet_task_info.start_cell,
            task_include_header=Google_sheet_task_info.include_header,
            task_query=Google_sheet_task_info.query,
            task_frequency=Google_sheet_task_info.frequency,
            run_time=Google_sheet_task_info.run_time,
        )
        session.add(new_task)
        session.commit()

    return None


# airflow will trigger this api


@data_suite_router.get("/run-google-sheet-task")
async def data_suite_run_google_sheet_task():
    # now 現在幾點
    now = int(datetime.now().strftime("%H"))
    print(now)
    print(type(now))

    with Session() as session:
        # daily
        run_task_daily = (
            session.query(DataSuiteTask)
            .filter(extract("hour", DataSuiteTask.run_time) == int(now))
            .filter(DataSuiteTask.task_frequency == "daily")
            .all()
        )
        if run_task_daily is not None:
            for task in run_task_daily:
                column_names, data = get_db(task.task_query, Session, -1)
                df = pd.DataFrame(data)

                gc = pygsheets.authorize(service_account_file="app/Credentials.json")
                wb = gc.open_by_url(task.task_url)
                sheet = wb.worksheet_by_title(task.task_sheet_name)
                write_to_google_sheet(
                    df, sheet, task.task_start_cell, task.task_include_header
                )

        # hourly
        run_task_hourly = (
            session.query(DataSuiteTask)
            .filter(DataSuiteTask.task_frequency == "hourly")
            .all()
        )
        if run_task_hourly is not None:
            for task in run_task_hourly:
                column_names, data = get_db(task.task_query, Session, -1)
                df = pd.DataFrame(data)

                gc = pygsheets.authorize(service_account_file="app/Credentials.json")
                wb = gc.open_by_url(task.task_url)
                sheet = wb.worksheet_by_title(task.task_sheet_name)
                write_to_google_sheet(
                    df, sheet, task.task_start_cell, task.task_include_header
                )


@data_suite_router.post("/add-workflow")
async def data_suite_add_workflow(workflow_info: WorkFlow):
    print(workflow_info)
    now = datetime.now()
    unix_timestamp = int(now.timestamp())

    print(now)
    with Session() as session:
        subtask = ",".join(workflow_info.work_flow_subtask)
        print(subtask)

        new_workflow = DataSuiteWorkFlow(
            work_flow_name=workflow_info.work_flow_name,
            work_flow_frequency=workflow_info.work_flow_frequency,
            last_modify_time=unix_timestamp,
            create_time=unix_timestamp,
            create_person=workflow_info.work_flow_person,
            work_flow_subtask=subtask,
            work_flow_status="active",
        )
        session.add(new_workflow)
        session.commit()

    return {"detail": "success"}


@data_suite_router.post("/run-workflow/{workflow_id}")
def data_suite_run_workflow(workflow_id: int):
    print(workflow_id)
    with Session() as session:
        workflow_session = (
            session.query(DataSuiteWorkFlow.work_flow_subtask)
            .filter(DataSuiteWorkFlow.pro_id == workflow_id)
            .first()
        )
        for subtask in workflow_session.work_flow_subtask.split(","):
            print(subtask)

    return {"detail": "success"}


@data_suite_router.get("/workflow")
def data_suite_get_workflow():
    with Session() as session:
        results = session.query(DataSuiteWorkFlow).all()

        data = [
            {
                "work_flow_name": result.work_flow_name,
                "work_flow_frequency": result.work_flow_frequency.split(",")[0],
                "last_run_time": unix_time_transformer(result.last_run_time),
                "last_run_status": "未執行"
                if result.last_run_status is None
                else result.last_run_status,
                "next_run_time": next_runtime_calculator(
                    result.work_flow_status, result.work_flow_frequency
                ),
                "last_modify_time": unix_time_transformer(result.last_modify_time),
                "create_time": unix_time_transformer(result.create_time),
                "create_person": result.create_person,
                "work_flow_subtask": result.work_flow_subtask,
                "work_flow_status": result.work_flow_status,
            }
            for result in results
        ]

    return {"worrkflow": data}
