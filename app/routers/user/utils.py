import os
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta


import pandas as pd
from sqlalchemy import desc, func
from typing import List
from fastapi import FastAPI, APIRouter, UploadFile, Form, File, Request, HTTPException, Path, Cookie
from jose import JWTError, jwt
from app.database.sqlalchemy import Session, engine


def create_access_token(user:str, expires_delta: int):

    # get env
    SECRET_KEY = os.getenv('SECRET_KEY')
    ALGORITHM = os.getenv('ALGORITHM')

    # expires_time
    expires_delta = datetime.utcnow() + timedelta(minutes=expires_delta)
    encoded_jwt = jwt.encode({'sub': user,
                              'exp': expires_delta,
                              'token_type': 'bearer',
                                    }, SECRET_KEY, ALGORITHM)
    return encoded_jwt

from passlib.context import CryptContext
from app.schemas.User import User
def authenticate_user(username: str, password: str):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    with Session() as session:
        user = session.query(User).filter(User.user_name == username).first()
        if not user:
            return False
        if not pwd_context.verify(password, user.user_password):
            return False
        return user


from jose.exceptions import ExpiredSignatureError
async def get_current_user(token: str = Cookie(None)):
    # get env
    SECRET_KEY = os.getenv('SECRET_KEY')
    ALGORITHM = os.getenv('ALGORITHM')
    print(f'Token: {token}')

    if token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")