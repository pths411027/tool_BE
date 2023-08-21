from typing import List

from fastapi import File, HTTPException, UploadFile
from pydantic import BaseModel, EmailStr, Field, validator


class RegisterUser(BaseModel):
    username: str = Field(..., example="Marcus Tsai")
    password: str = Field(..., example="1234")
    email: str = Field(..., example="marcus.tsai@shopp.com")
