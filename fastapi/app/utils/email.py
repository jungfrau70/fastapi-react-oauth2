from typing import List

from models import User
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
import jwt

from common.config import get_settings

SITE_URL = get_settings().SITE_URL
SITE_NAME = get_settings().SITE_NAME
SECRET_KEY = get_settings().SECRET_KEY
ALGORITHM = get_settings().ALGORITHM

PROTOCOL = get_settings().PROTOCOL
FULL_HOST_NAME = get_settings().FULL_HOST_NAME
PORT_NUMBER = get_settings().PORT_NUMBER
API_LOCATION = f"{PROTOCOL}{FULL_HOST_NAME}:{PORT_NUMBER}"


conf = ConnectionConfig(
    MAIL_USERNAME=get_settings().MAIL_USERNAME,
    MAIL_PASSWORD=get_settings().MAIL_PASSWORD,
    MAIL_FROM=get_settings().MAIL_FROM,
    MAIL_PORT=get_settings().MAIL_PORT,
    MAIL_SERVER=get_settings().MAIL_SERVER,
    MAIL_STARTTLS=get_settings().MAIL_STARTTLS,
    MAIL_SSL_TLS=get_settings().MAIL_SSL_TLS,
    USE_CREDENTIALS=get_settings().USE_CREDENTIALS,
    VALIDATE_CERTS=get_settings().VALIDATE_CERTS
)


async def send_mail(email: List[EmailStr], instance: User):
    """send Account Verification mail"""

    token_data = {
        "id": str(instance.id),
        "username": instance.username,
        "email": instance.email,
    }

    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
    </head>
    <body>
        <div style = "display:flex; align-items: center; flex-direction: column" >
            <h3>Account Verification</H3>

            <br>

            <p>
                Thanks for joining us, please click on the button below
                to verify your account
            </p> 
            
            <a style = "display:marign-top: 1rem ; padding: 1rem; border-redius: 0.5rem;
             font-size:1rem; text-decoration: no; background: #0275d8; color:white"
             href="{SITE_URL}/verification/?token={token}">
                Verify your email
             </a>
        </div>
    </body>
    </html>
    """
    # print(f"""

    # your mail:
    # {SITE_URL}verification/email/?token={token}

    # """)

    message = MessageSchema(
        subject=SITE_NAME + " account verification",
        recipients=email,  # List of recipients,
        body=template,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
