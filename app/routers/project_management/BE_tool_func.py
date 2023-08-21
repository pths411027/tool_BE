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
