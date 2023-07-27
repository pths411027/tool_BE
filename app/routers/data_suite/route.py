import os
from datetime import datetime
from fastapi import FastAPI, APIRouter, UploadFile, Form, File, Request, HTTPException
from app.database.sqlalchemy import Session, engine
import json
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()

data_suite_router = APIRouter(tags=["Data Suite"], prefix="/data-suite")


@data_suite_router.get("/home")
async def data_suite_home():
    return {"data_suite_router": "home"}

# add main project
from pydantic import BaseModel, Field
class Query_info(BaseModel):
    query: str = Field(..., example="select * from users")
    


import sqlparse
from app.routers.data_suite.utils import get_db

@data_suite_router.post("/query")
async def data_suite_query(query_info: Query_info):
    print(query_info)
    column_names, data = get_db(query_info.query, Session, 10)  
    if column_names == 400:
        raise HTTPException(status_code=400, detail=data)
    else:
        return {"column_names": list(column_names),  "data": data[:5]}


from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse

import io
import pandas as pd

@data_suite_router.post("/download")
async def data_suite_download(query_info: Query_info):
    column_names, data = get_db(query_info.query, Session, 10)
    if column_names == 400:
        raise HTTPException(status_code=400, detail=data)
    else:
        df = pd.DataFrame(data)
        #csv_data = "\n".join([",".join(map(str, row.values())) for row in data])
    # 給我現在時間
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=query_output.csv"
    response.headers["output-filename"] = "=query_output.csv"
    return response



from sqlalchemy import MetaData
from app.database.sqlalchemy import Base
@data_suite_router.get("/table")
async def data_suite_table():
    table_list = list(Base.metadata.tables.keys())
    return {'table_list':table_list}