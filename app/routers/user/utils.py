import os
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from passlib.context import CryptContext

from app.database.sqlalchemy import Session
from app.schemas.WL import WLMember


def create_access_token(user: dict, expires_delta: int) -> str:
    # get env
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

    # prod: long expires time
    # expires_delta = datetime.utcnow() + timedelta(minutes=expires_delta)
    # dev: short expires time
    expires_delta = datetime.utcnow() + timedelta(minutes=100)
    encoded_jwt = jwt.encode(
        {
            "sub": user["member_name"],
            "exp": expires_delta,
            "id": user["member_id"],
            "level": user["member_level"],
        },
        SECRET_KEY,
        ALGORITHM,
    )
    return encoded_jwt


def authenticate_user(form_data: OAuth2PasswordRequestForm):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    with Session() as session:
        user = (
            session.query(
                WLMember.member_name,
                WLMember.member_id,
                WLMember.member_level,
                WLMember.member_password,
            )
            .filter(WLMember.member_email == form_data.username)
            .first()
        )
        if not user:
            return None
        elif not pwd_context.verify(form_data.password, user.member_password):
            return None
        else:
            return {
                "member_name": user.member_name,
                "member_id": user.member_id,
                "member_level": user.member_level,
            }


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    # get env
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
