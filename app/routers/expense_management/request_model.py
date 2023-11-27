from pydantic import BaseModel, Field
from uuid import UUID


class AddExpense(BaseModel):
    expense_id: UUID = Field(
        default_factory=UUID, example="123e4567-e89b-12d3-a456-426614174000"
    )
    expense_name: str = Field(..., example="test")
    expense_type: str = Field(..., example="test")
    expense_amount: int = Field(..., example=1)
    expense_time: int = Field(..., example=1)
