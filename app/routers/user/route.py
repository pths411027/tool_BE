from dotenv import load_dotenv
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext

from app.database.sqlalchemy import Session
from app.routers.user.request_model import RegisterUser
from app.routers.user.utils import (
    authenticate_user,
    create_access_token,
    get_current_user,
)
from app.schemas.WL import WLMember

load_dotenv()
app = FastAPI()

user_router = APIRouter(tags=["User"], prefix="/user")


@user_router.get("/home")
async def user_home():
    return {"user_router": "home"}


@user_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_info: RegisterUser):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(user_info.member_password)

    with Session() as session:
        existing_member = (
            session.query(WLMember).filter_by(member_name=user_info.member_name).first()
        )

        if existing_member:
            raise HTTPException(
                status_code=400,
                detail=f"Member_{user_info.member_name} already exists",
            )
        else:
            new_member = WLMember(
                member_name=user_info.member_name,
                member_photo=user_info.member_photo,
                member_password=hashed_password,
                member_email=user_info.member_email + user_info.member_email_type,
                team_id=0,
                member_level=user_info.member_level,
            )
        session.add(new_member)
        session.commit()

    return {"detail": f"{user_info.member_name} has registered successfully"}


@user_router.post("/token", status_code=status.HTTP_200_OK)
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user=user, expires_delta=30)

    return {"access_token": access_token, "token_type": "bearer"}


@user_router.get("/status", status_code=status.HTTP_200_OK)
async def check_login_status(user: str = Depends(get_current_user)):
    return {"isLoggedIn": True, "user": user}
