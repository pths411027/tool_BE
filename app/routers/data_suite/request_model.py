from pydantic import BaseModel, Field, EmailStr, validator
from fastapi import UploadFile, HTTPException
from typing import List
from datetime import time
from enum import Enum

class Query_info(BaseModel):
    query: str = Field(..., example="select * from users")

class Google_sheet(BaseModel):
    query: str = Field(..., example="select * from users")
    task_name: str = Field(..., example="task_name")
    url: str = Field(..., example="https://docs.google.com/spreadsheets/d/1bTB4Bcfe_UcyezkWX86_GcyHqZhnINF2Huf0Qj9Jixo/edit?hl=zh-TW#gid=1028956026")
    sheet_name: str = Field(..., example="工作表1")
    start_cell: str = Field(..., example="A1")
    include_header: bool = Field(..., example=True)
    
class Fequency(str, Enum):
    daily = "daily"
    hourly = "hourly"
    

class Google_sheet_task(BaseModel):
    query: str = Field(..., example="select * from users")
    task_name: str = Field(..., example="task_name")
    url: str = Field(..., example="https://docs.google.com/spreadsheets/d/1bTB4Bcfe_UcyezkWX86_GcyHqZhnINF2Huf0Qj9Jixo/edit?hl=zh-TW#gid=1028956026")
    sheet_name: str = Field(..., example="工作表1")
    start_cell: str = Field(..., example="A1")
    include_header: bool = Field(..., example=True)
    frequency: str = Field(..., example="daily")
    run_time: time = Field(..., example="03:00:00")