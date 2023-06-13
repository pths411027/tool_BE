from pydantic import BaseModel, Field
from fastapi import UploadFile
from typing import List

class AddMainProject(BaseModel):
    projectName: str = Field(..., example="後端")
    KYC: str = Field(..., example="Marcus")
    tag: str = Field(..., example="CICD")
    description: str = Field(..., example="工作內容詳細敘述")
    startDay: str = Field(..., example="2023-06-13")
    endDay: str = Field(..., example="2023-06-13")
    extraInputs: List[List[str]] = Field(..., example=[["工作", "快工作", "快快工作"]])
