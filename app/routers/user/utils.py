import json
import os
from datetime import datetime, timedelta
from typing import List

import pandas as pd
from dotenv import load_dotenv
from fastapi import (APIRouter, Cookie, FastAPI, File, Form, HTTPException,
                     Path, Request, UploadFile)
from jose import JWTError, jwt
from sqlalchemy import desc, func

from app.database.sqlalchemy import Session, engine


def create_access_token(user: str, expires_delta: int):
    # get env
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

    # expires_time
    expires_delta = datetime.utcnow() + timedelta(minutes=expires_delta)

    encoded_jwt = jwt.encode(
        {
            "sub": user,
            "exp": expires_delta,
        },
        SECRET_KEY,
        ALGORITHM,
    )
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


from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose.exceptions import ExpiredSignatureError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    # get env
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    if token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
