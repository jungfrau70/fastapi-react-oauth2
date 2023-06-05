"""
1. 구글 로그인을 위한 구글 앱 준비 (구글 개발자 도구)
2. FB 로그인을 위한 FB 앱 준비 (FB 개발자 도구)
3. 카카오 로그인을 위한 카카오 앱준비( 카카오 개발자 도구)
4. 이메일, 비밀번호로 가입 (v)
5. 가입된 이메일, 비밀번호로 로그인, (v)
6. JWT 발급 (v)

7. 이메일 인증 실패시 이메일 변경
8. 이메일 인증 메일 발송
9. 각 SNS 에서 Unlink 
10. 회원 탈퇴
11. 탈퇴 회원 정보 저장 기간 동안 보유(법적 최대 한도 내에서, 가입 때 약관 동의 받아야 함, 재가입 방지 용도로 사용하면 가능)

400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
405 Method not allowed
500 Internal Error
502 Bad Gateway 
504 Timeout
200 OK
201 Created

"""
# response_classes


# signals

# image upload


import bcrypt
import jwt

from datetime import datetime, timedelta
from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, JSONResponse, HTMLResponse
from starlette.requests import Request

from app.models import SnsType, Token, UserToken
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi import status

from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)

from passlib.context import CryptContext
from app.models import *

# templates
from fastapi.templating import Jinja2Templates

import httplib2
from oauth2client import client

from app.models import *
from app.configs import Configs

SECRET_KEY = Configs.SECRET_KEY
ALGORITHM = Configs.ALGORITHM

GOOGLE_OAUTH2_CLIENT_ID = Configs.GOOGLE_OAUTH2_CLIENT_ID
GOOGLE_OAUTH2_CLIENT_SECRET_JSON = Configs.GOOGLE_OAUTH2_CLIENT_SECRET_JSON

SWAP_TOKEN_ENDPOINT = Configs.SWAP_TOKEN_ENDPOINT
ACCESS_TOKEN_EXPIRE_MINUTES = Configs.ACCESS_TOKEN_EXPIRE_MINUTES
# COOKIE_AUTHORIZATION_NAME = Configs.COOKIE_AUTHORIZATION_NAME
# COOKIE_DOMAIN = Configs.COOKIE_DOMAIN
SECRET_KEY = Configs.SECRET_KEY
ALGORITHM = Configs.ALGORITHM
PROTOCOL = Configs.PROTOCOL
FULL_HOST_NAME = Configs.FULL_HOST_NAME
PORT_NUMBER = Configs.PORT_NUMBER

router = APIRouter(
    prefix="",
    tags=['Authentication']
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
# config_credentials = dotenv_values(".env")
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


async def is_email_exist(email: str):
    get_email = await User.get(email=email)
    if get_email:
        return True
    return False

def very_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(email, password):
    user = await User.get(email=email)
    if user and very_password(password, user.password):
        return user
    return False


async def authenticate_user_email(email):
    user = await User.get(email=email)
    if user:
        return user
    return False


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def token_generator(email: str, password: str):
    user = await authenticate_user(email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username(=email) or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    if user.is_verified:
        obj = await UserProfile.filter(owner_id=user.id).first()
        token_data = {
            "id": str(user.id),
            "email": user.email,
            "device_id": obj.device_id,
        }
        # token = jwt.encode(token_data, config_credentials['SECRET_KEY'])
        token = jwt.encode(token_data, SECRET_KEY)
        return token
    else:
        return {
            "status": "error",
            "message": "not verified"
        }

templates = Jinja2Templates(directory="templates")

@router.post("/token")
async def login(request_form: OAuth2PasswordRequestForm = Depends()):
    token = await token_generator(request_form.username, request_form.password)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/token/{sns_type}")
async def login(sns_type: SnsType, request_form: OAuth2PasswordRequestForm = Depends()):
    if sns_type == SnsType.email:
        token = await token_generator(request_form.username, request_form.password)
        return {"access_token": token, "token_type": "bearer"}
    print(sns_type)
    if sns_type ==  SnsType.google:
        print("1")
        return await HTMLResponse(google_login_javascript_server)
        # return {
        #     "status": "ok",
        #     "data": html
        # }
        # '''
        # get token from social login
        # '''

@router.get("/google_login_client")
def google_login_client():

    return HTMLResponse(google_login_javascript_client)


@router.get("/google_login_server")
def google_login_server():
    return HTMLResponse(google_login_javascript_server)


@router.post(f"{SWAP_TOKEN_ENDPOINT}", response_model=Token)
async def swap_token(request: Request = None):
    if not request.headers.get("X-Requested-With"):
        raise HTTPException(status_code=400, detail="Incorrect headers")

    google_client_type = request.headers.get("X-Google-OAuth2-Type")

    if google_client_type == 'server':
        try:
            body_bytes = await request.body()
            auth_code = jsonable_encoder(body_bytes)

            credentials = client.credentials_from_clientsecrets_and_code(
                CLIENT_SECRETS_JSON, ["profile", "email"], auth_code
            )

            http_auth = credentials.authorize(httplib2.Http())

            email = credentials.id_token["email"]

        except:
            raise HTTPException(status_code=400, detail="Unable to validate social login")


    if google_client_type == 'client':
        body_bytes = await request.body()
        auth_code = jsonable_encoder(body_bytes)

        try:
            idinfo = id_token.verify_oauth2_token(auth_code, requests.Request(), CLIENT_ID)

            # Or, if multiple clients access the backend server:
            # idinfo = id_token.verify_oauth2_token(token, requests.Request())
            # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
            #     raise ValueError('Could not verify audience.')

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            # If auth request is from a G Suite domain:
            # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
            #     raise ValueError('Wrong hosted domain.')

            if idinfo['email'] and idinfo['email_verified']:
                email = idinfo.get('email')

            else:
                raise HTTPException(status_code=400, detail="Unable to validate social login")

        except:
            raise HTTPException(status_code=400, detail="Unable to validate social login")


    # authenticated_user = await authenticate_user_email(email)
    authenticated_user = authenticate_user_email(email)

    if not authenticated_user:
        raise HTTPException(status_code=400, detail="Incorrect email address")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": authenticated_user.email}, expires_delta=access_token_expires
    )

    token = jsonable_encoder(access_token)

    response = JSONResponse({"access_token": token, "token_type": "bearer"})

    response.set_cookie(
        COOKIE_AUTHORIZATION_NAME,
        value=f"Bearer {token}",
        domain=COOKIE_DOMAIN,
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    return response