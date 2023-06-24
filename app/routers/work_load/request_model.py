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
    memberName: str = Field(..., example="Marcus Tsai")
    memberPhoto: str = Field(..., example="old-man")
    memberEmail: str = Field(..., example="Marcus.tsai")
    memberEmailType: str = Field(..., example="@shopee.com")
    memberLevel: str = Field(..., example="Entry")
    

class AddFile(BaseModel):
    pro_id: int = Field(..., example=3)

