from typing import List
from datetime import datetime
from pydantic import BaseModel, Field


class AddMainProject(BaseModel):
    project_name: str = Field(..., example="3C電子產品部門_資訊")
    team_id: int = Field(..., example=1)
    project_KPI: int = Field(..., example=300)
    # project_status: int = Field(..., example=1)
    option_inputs: List[List[str]] = Field(..., example=[["完成", True, "red"]])
    customer_inputs: List[List[str]] = Field(..., example=[["Remark", "int", "寫註解"]])
    distinct_inputs: List[List[str]] = Field(..., example=[["ItemID"], ["Ctime"]])


class AddFile(BaseModel):
    project_id: int = Field(..., example=3)


class AddTeam(BaseModel):
    team_name: str = Field(..., example="3C電子產品部門")
    manager: int = Field(..., example=1)
    member_list: List[int] = Field(..., example=[2, 6])


class AskTask(BaseModel):
    project_id: int = Field(..., example=1)
    member_id: int = Field(..., example=1)


class SubmitTask(BaseModel):
    file_id: int = Field(..., example=1)
    file_status: int = Field(..., example=1)
    file_priority: int = Field(..., example=1)


class SubmitAnswer(BaseModel):
    data_id: int = Field(..., example=1)
    option_id: int = Field(..., example=9)
    customer_answer: str = Field(..., example="test")


class SubmitRequest(BaseModel):
    # member_id: int = Field(..., example=1)
    project_id: int = Field(..., example=1)
    answers: List[SubmitAnswer] = Field(
        ...,
        example=[
            {"data_id": 1, "option_id": 9, "customer_answer": "test_1"},
            {"data_id": 2, "option_id": 10, "customer_answer": "test_2"},
        ],
    )


class SubmitKPI(BaseModel):
    KPI_start_time: datetime = Field(..., example="2023-07-01T10:30:00")
    KPI_end_time: datetime = Field(..., example="2023-07-01T11:45:00")
    KPI_content: str = Field(..., example="test")
    KPI_amount: int = Field(..., example=1)
