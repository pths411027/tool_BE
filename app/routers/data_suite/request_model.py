from datetime import time
from enum import Enum
from typing import List

from fastapi import HTTPException, UploadFile
from pydantic import BaseModel, EmailStr, Field, validator


class Query_info(BaseModel):
    query: str = Field(..., example="select * from users")


class Google_sheet(BaseModel):
    query: str = Field(..., example="select * from users")
    task_name: str = Field(..., example="task_name")
    url: str = Field(
        ...,
        example="https://docs.google.com/spreadsheets/d/1bTB4Bcfe_UcyezkWX86_GcyHqZhnINF2Huf0Qj9Jixo/edit?hl=zh-TW#gid=1028956026",
    )
    sheet_name: str = Field(..., example="工作表1")
    start_cell: str = Field(..., example="A1")
    include_header: bool = Field(..., example=True)


class Fequency(str, Enum):
    daily = "daily"
    hourly = "hourly"


class Google_sheet_task(BaseModel):
    query: str = Field(..., example="select * from users")
    task_name: str = Field(..., example="task_name")
    url: str = Field(
        ...,
        example="https://docs.google.com/spreadsheets/d/1bTB4Bcfe_UcyezkWX86_GcyHqZhnINF2Huf0Qj9Jixo/edit?hl=zh-TW#gid=1028956026",
    )
    sheet_name: str = Field(..., example="工作表1")
    start_cell: str = Field(..., example="A1")
    include_header: bool = Field(..., example=True)
    frequency: str = Field(..., example="daily")
    run_time: time = Field(..., example="03:00:00")


class WorkFlow(BaseModel):
    work_flow_name: str = Field(..., example="daily_update")
    work_flow_frequency: str = Field(..., example="daily, 13")
    work_flow_subtask: List[str] = Field(..., example=[1, 2, 3])
    work_flow_person: str = Field(..., example="marcus")
