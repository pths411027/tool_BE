from pydantic import BaseModel, Field, EmailStr, validator
from fastapi import UploadFile, HTTPException
from typing import List

class Query_info(BaseModel):
    query: str = Field(..., example="select * from users")

class Google_sheet(BaseModel):
    query: str = Field(..., example="select * from users")
    task_name: str = Field(..., example="task_name")
    url: str = Field(..., example="https://docs.google.com/spreadsheets/d/1bTB4Bcfe_UcyezkWX86_GcyHqZhnINF2Huf0Qj9Jixo/edit?hl=zh-TW#gid=1028956026")
    sheet_name: str = Field(..., example="工作表1")
    start_cell: str = Field(..., example="A1")
    include_header: bool = Field(..., example=True)
    