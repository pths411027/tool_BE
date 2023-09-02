from typing import List

from fastapi import File, HTTPException, UploadFile
from pydantic import BaseModel, EmailStr, Field, validator


class AddMainProject(BaseModel):
    projectName: str = Field(..., example="3C電子產品部門_資訊")
    team: str = Field(..., example="3C電子產品部門")
    KPI: str = Field(..., example="300")
    optionInputs: List[List[str]] = Field(..., example=[["完成", True, "red"]])
    customerInputs: List[List[str]] = Field(..., example=[["Remark", "int", "寫註解"]])
    distinctInputs: List[List[str]] = Field(..., example=[["ItemID"], ["Ctime"]])


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


class AddTeam(BaseModel):
    teamName: str = Field(..., example="3C電子產品部門")
    manager: int = Field(..., example=1)
    memberList: List[int] = Field(..., example=[2, 6])


class AskTask(BaseModel):
    project_id: int = Field(..., example=1)
    member_id: int = Field(..., example=1)


class SubmitTask(BaseModel):
    file_id: int = Field(..., example=1)
    file_status: int = Field(..., example=1)
    file_priority: int = Field(..., example=1)


class SubmitAnswer(BaseModel):
    id: int = Field(..., example=1)
    option_id: int = Field(..., example=9)
    customer_answer: str = Field(..., example="test")


class SubmitRequest(BaseModel):
    member_id: int = Field(..., example=1)
    answers: List[SubmitAnswer] = Field(
        ...,
        example=[
            {"id": 1, "option_id": 9, "customer_answer": "test_1"},
            {"id": 2, "option_id": 10, "customer_answer": "test_"},
        ],
    )
