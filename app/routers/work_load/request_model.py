from pydantic import BaseModel, Field, EmailStr, validator
from fastapi import UploadFile, HTTPException
from typing import List
import re

class AddMainProject(BaseModel):
    projectName: str = Field(..., example="後端")
    KYC: str = Field(..., example="Marcus")
    tag: str = Field(..., example="CICD")
    description: str = Field(..., example="工作內容詳細敘述")
    startDay: str = Field(..., example="2023-06-13")
    endDay: str = Field(..., example="2023-06-13")
    extraInputs: List[List[str]] = Field(..., example=[["工作", "快工作", "快快工作"]])

class AddMember(BaseModel):
    chineseName: str = Field(..., example="蔡漢錩")
    englishName: str = Field(..., example="Marcus")
    email: str = Field(..., example="marcus.tsai@shopee.com")
    department: str = Field(..., example="OPS-BI")
    team: str = Field(..., example="DPD")
    level: str = Field(..., example="SE")
    manager: List[str]= Field(..., example=["Aaron", "Lu", "Tiny"])

    @validator('email')
    def email_must_be_shopee(cls, v):
        if not "@shopee.com" in v:
            raise HTTPException(status_code=400, detail='請填入正確的蝦皮信箱')
        return v

    
