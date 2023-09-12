import logging.config
from typing import Union

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from app.database.sqlalchemy import Session

from .routers import routers
from .settings.logging import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)


app_logger = logging.getLogger("app")


# 設定環境參數
load_dotenv()

app = FastAPI(debug=True)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="user/token",
)


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


# 設置跨域中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # You can specify allowed origins, e.g. ["http://localhost:8000"]
    allow_credentials=True,
    allow_methods=["*"],  # You can specify allowed methods, e.g. ["GET", "POST"]
    allow_headers=["*"],  # You can specify allowed headers, e.g. ["Content-Type"]
)

for router in routers:
    app.include_router(router=router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(
    item_id: int,
    q: Union[str, None] = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    return {"item_id": item_id, "q": q}
