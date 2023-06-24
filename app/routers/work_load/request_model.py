from pydantic import BaseModel, Field, EmailStr, validator
from fastapi import UploadFile, HTTPException, File
from typing import List

class AddMainProject(BaseModel):
    projectName: str = Field(..., example="3C電子產品部門_資訊")
    team: str = Field(..., example="3C電子產品部門")
    KPI: str = Field(..., example="300")
    optionInputs: List[List[str]] = Field(..., example=[["完成", True, "red"]])
    customerInputs: List[List[str]] = Field(..., example=[["Remark", "int", "寫註解"]])

class AddTeam(BaseModel):
    teamName: str = Field(..., example="3C電子產品部門")

class AddMember(BaseModel):
    englishName: str = Field(..., example="Marcus Tsai")
    email: str = Field(..., example="marcus.tsai@shopee.com")
    team: str = Field(..., example="3C電子產品部門")
    level: str = Field(..., example="SE")

class AddFile(BaseModel):
    pro_id: int = Field(..., example=3)