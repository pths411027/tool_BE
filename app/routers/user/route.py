import os
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta


import pandas as pd
from sqlalchemy import desc, func
from typing import List

from fastapi import FastAPI, APIRouter, UploadFile, Form, File, Request, HTTPException, Path, Query, Depends, status
from jose import JWTError, jwt

from app.database.sqlalchemy import Session, engine
from app.routers.user.utils import create_access_token

load_dotenv()
app = FastAPI()

user_router = APIRouter(tags=["User"], prefix="/user")

@user_router.get("/home")
async def user_home():
    return {"user_router": "home"}







from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm



from app.routers.user.request_model import RegisterUser
from app.schemas.User import User
@user_router.post("/register")
async def register_user(user_info: RegisterUser = Depends()):

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(user_info.password)
    
    with Session() as session:
        # check if user exist
        user = session.query(User).filter(User.user_name == user_info.username).first()
        if user:
            raise HTTPException(status_code=400, detail="Username already registered")
        else:
            new_user = User(user_name=user_info.username,
                            user_password=hashed_password,
                            user_email=user_info.email
                            )
            session.add(new_user)
            session.commit()
    return {'detail': f'{user_info.username} registered successfully'}
    

from app.routers.user.utils import authenticate_user

@user_router.post("/token")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    user  = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"}
                            )
    access_token = create_access_token(
        user.user_name, expires_delta=30
    )
    return {"access_token": access_token, "token_type": "bearer"}
from app.routers.user.utils import get_current_user
    

@user_router.get("/status")
async def check_login_status(user:str = Depends(get_current_user)):
    return {"isLoggedIn": True}
