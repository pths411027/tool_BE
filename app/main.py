from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging.config
from .settings.logging import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)

from .routers import routers
app_logger = logging.getLogger('app')


app = FastAPI(debug=True)
# 設置跨域中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify allowed origins, e.g. ["http://localhost:8000"]
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
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}