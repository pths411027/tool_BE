from pydantic import BaseModel, Field, EmailStr, validator
from fastapi import UploadFile, HTTPException, File
from typing import List

class RegisterUser(BaseModel):
    username: str = Field(..., example="Marcus Tsai")
    password: str = Field(..., example="1234")
    #vemail: str = Field(..., example="marcus.tsai@shopp.com")
    


    

