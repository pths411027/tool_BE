from pydantic import BaseModel, Field


class RegisterUser(BaseModel):
    member_name: str = Field(..., example="Marcus Tsai")
    member_photo: str = Field(..., example="oldman")
    member_email: str = Field(..., example="Marcus.tsai")
    member_email_type: str = Field(..., example="@shopee.com")
    member_password: str = Field(..., example="1234")
    member_level: str = Field(..., example="Entry")
