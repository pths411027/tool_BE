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
