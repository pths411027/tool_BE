# 寄信函式
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def Send(
    smtp_ssl_host,
    smtp_ssl_port,
    username,
    password,
    email_subject,
    email_body,
    email_to,
):
    msg = MIMEMultipart()
    msg["Subject"] = email_subject
    msg["From"] = username
    msg["To"] = ", ".join(email_to)
    person = ""
    for man in email_to:
        person += man.split("@")[0] + ", "

    body = f"Hi {person[:-2]}，\n\n{email_body}"
    message = MIMEText(body, "plain")
    msg.attach(message)
    smtp_tls = True
    try:
        with smtplib.SMTP(smtp_ssl_host, smtp_ssl_port) as smtp:
            if smtp_tls:
                smtp.starttls()
            smtp.login(username, password)
            smtp.sendmail(username, email_to, msg.as_string())
        print(f"失敗信件寄出成功")
    except Exception as e:
        print(f"例外信件發送錯誤: {e}")


from datetime import datetime
import os

import magic

from app.schemas.WL import WLFile


async def process_file(file, pro_id: int, Session):
    file_content = await file.read()
    file_mime = magic.from_buffer(file_content, mime=True)
    file_extention = os.path.splitext(file.filename)[1]
    created_time = datetime.now().replace(microsecond=0)
    file_size_kb = len(file_content) / 1024

    with Session() as session:
        new_file = WLFile(
            file_name=file.filename,
            created_time=created_time,
            project_id=pro_id,
            file_data=file_content,
            file_type=file_mime,
            file_extension=file_extention,
            file_size=file_size_kb,
            file_finish=False,
        )
        session.add(new_file)
        session.commit()


import pandas as pd
from io import BytesIO
from app.schemas.WL import WLData
from app.schemas.WL import WLMainProject
import sys
from sqlalchemy import func


async def process_file_excel(file, pro_id: int, Session, first_upload: bool):
    file_content = await file.read()
    file_mime = magic.from_buffer(file_content, mime=True)
    file_extention = os.path.splitext(file.filename)[1]
    created_time = int(datetime.now().replace(microsecond=0).timestamp())
    file_size_kb = len(file_content) / 1024
    df = pd.read_excel(BytesIO(file_content), engine="openpyxl")

    if first_upload == True:
        print("first upload")
        # df = pd.read_excel(BytesIO(file_content), engine="openpyxl")
        col_format = df.columns.tolist()
        col_format = "|".join(col_format)
        with Session() as session:
            session.query(WLMainProject).filter(
                WLMainProject.project_id == pro_id
            ).update({WLMainProject.file_format: col_format})
            session.commit()

        print(col_format)
    else:
        print("not first upload")

    with Session() as session:
        # get distinct col
        distinct_col = (
            session.query(WLMainProject)
            .filter(WLMainProject.project_id == pro_id)
            .first()
        )
        distinct_col = distinct_col.distinct_col.split("|")
        print(distinct_col)

        max_priority = (
            session.query(func.max(WLFile.file_priority))
            .filter(WLFile.project_id == pro_id)
            .scalar()
        )
        max_priority = max_priority + 1 if max_priority else 1

        # TODO:check format
        new_file = WLFile(
            file_name=file.filename,
            created_time=created_time,
            project_id=pro_id,
            # file_data=file_content,
            file_type=file_mime,
            file_extension=file_extention,
            file_size=file_size_kb,
            file_finish=False,
            file_status=1,
            file_priority=max_priority,
        )
        session.add(new_file)
        session.flush()

        new_file_id = new_file.file_id

        df["data"] = df.apply(lambda row: "|".join(row.astype(str)), axis=1)
        df["distinct_detemine"] = df[distinct_col].apply(
            lambda row: "|".join(row.astype(str)), axis=1
        )

        for i in df.index:
            new_row = WLData(
                file_id=new_file_id,
                row_id=i,
                row_data=df["data"][i],
                completed=False,
                modify_time=created_time,
                distinct_detemine=df["distinct_detemine"][i],
            )
            session.add(new_row)
        session.commit()
