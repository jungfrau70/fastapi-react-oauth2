# response_classes
import jwt
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Depends, Request, HTTPException, status
from starlette.responses import JSONResponse

# # Authentication
# from authentication import (
#     get_hashed_password,
#     very_token,
#     token_generator
# )
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)

# signals
from tortoise import BaseDBAsyncClient
from tortoise.signals import post_save
from typing import List, Optional, Type

# templates
from fastapi.templating import Jinja2Templates

# image upload
from fastapi import File, UploadFile
import secrets
from PIL import Image

# middleware
from fastapi.middleware.cors import CORSMiddleware

# model
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from passlib.context import CryptContext

from app.models import *
from ..utils.email import (
    send_mail
)

from app.models import *

from  app.configs import Configs
SECRET_KEY = Configs.SECRET_KEY
ALGORITHM = Configs.ALGORITHM

router = APIRouter(
    prefix="",
    tags=['User']
)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')

def get_hashed_password(password):
    return pwd_context.hash(password)


async def very_token(token: str):
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM])
        user = await User.get(email=payload.get("email"))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=['HS256'])
        user = await User.get(email=payload.get("email"))
        # user.last_login_time = round(datetime.timestamp(datetime.utcnow))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username(=email) or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )
    return await user


#####################################################
# CRUD functioinality
#####################################################


@post_save(User)
async def create_play(
    sender: "Type[User]",
    instance: User,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str]
) -> None:
    if created:
        # # send the email
        await send_mail([instance.email], instance)

        t_now = datetime.utcnow()
        expiration_date = t_now + relativedelta(years=+100)
        created_at = round(datetime.timestamp(t_now))

        user_profile_obj = await UserProfile.create(
            play_ticket=100,
            created_at=created_at,
            owner=instance
        )
        await pydantic_user_profile.from_tortoise_orm(user_profile_obj)

        # product_purchase_obj = await ProductPurchase.create(
        #     level=100,
        #     purchase_date=round(datetime.timestamp(t_now)),
        #     expiration_date=round(datetime.timestamp(expiration_date)),
        #     owner=instance
        # )
        # await pydantic_product_purchase.from_tortoise_orm(product_purchase_obj)

        level_purchase_obj = await LevelPurchase.create(
            level=100,
            purchase_date=round(datetime.timestamp(t_now)),
            expiration_date=round(datetime.timestamp(expiration_date)),
            owner=instance
        )
        await pydantic_level_purchase.from_tortoise_orm(level_purchase_obj)

        # stage_clear_obj = await StageClear.create(
        #     stage='s1000',
        #     gain_star='False',
        #     owner=instance
        # )
        # await pydantic_stage_clear.from_tortoise_orm(stage_clear_obj)

        play_data_obj = await PlayData.create(
            block_use_count=0,
            card_use_count=0,
            stage_clear_count=0,
            stage_play_count=0,
            owner=instance
        )
        await pydantic_play_data.from_tortoise_orm(play_data_obj)

        achieve_obj = await Achievement.create(
            achieve_data='',
            owner=instance
        )
        await pydantic_achieve.from_tortoise_orm(achieve_obj)

        # ar_view_obj = await ARView.create(
        # ...
        #     owner=instance
        # )
        # await pydantic_ar_view.from_tortoise_orm(ar_view_obj)

    # # send the email
    # await send_mail([instance.email], instance)

async def is_email_exist(email: str):
    get_email = await User.get(email=email)
    if get_email:
        return True
    return False


@router.post("/register/{sns_type}")
async def register(sns_type: SnsType, user: pydantic_user_in):

    """
    `회원가입 API`\n
    :param sns_type\n
    :param user_info\n
    :return status
    """
    try:
        print("1")
        user_info = user.dict(exclude_unset=True)
        print("2")
        if sns_type == SnsType.email:
            print("3")
            try:
                if await is_email_exist(user_info["email"]):
                    return JSONResponse(status_code=400, content=dict(msg="EMAIL_EXISTS"))
            except:
                pass
            print("4")
            user_info["password"] = get_hashed_password(user_info["password"])
            print("5")
            
            # t_now = datetime.utcnow()
            # user_info["created_at"] = round(datetime.timestamp(t_now))
            # user_info["login_count"] = 0
            print(user_info)
            # user_obj = ''
            try:
                user_obj = await User.create(**user_info)
                print("6")
            except Exception as e:
                print(e)
            # print(user_obj)
            print("7")
            # new_user = await pydantic_user.from_queryset(email=user_info["email"])
            new_user = await User.get(email=user_info["email"])
            print("8")
            return {
                "status": "ok",
                "data": f"Hello {new_user.username}, thanks for joining to Coding&Play. Please check your email inbox, and click the link to confirm your registration"
            }
        else:
            return {
                "status": "ok",
                "data": f"Hello {new_user.username}, under construction"
            }

    except Exception as e:
        print(e)
        
# @router.post("/registration")
# async def user_registration(user: pydantic_user_in):
#     user_info = user.dict(exclude_unset=True)
#     user_info["password"] = get_hashed_password(user_info["password"])
#     t_now = datetime.utcnow()
#     user_info["created_at"] = round(datetime.timestamp(t_now))
#     # print(user_info["created_at"])
#     user_obj = await User.create(**user_info)
#     # print(user_obj.created_at)
#     new_user = await pydantic_user.from_tortoise_orm(user_obj)
#     return {
#         "status": "ok",
#         "data": f"Hello {new_user.username}, thanks for joining to Coding&Play. Please check your email inbox, and click the link to confirm your registration"
#     }

templates = Jinja2Templates(directory="templates")


@router.get("/verification", response_class=HTMLResponse)
async def email_verification(request: Request, token: str):
    user = await very_token(token)

    if user and not user.is_verified:
        user.is_verified = True
        await user.save()
        return templates.TemplateResponse("verification.html", {
            "request": request,
            "username": user.username,
        })
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expried token",
            headers={"WWW-Authenticate": "Bearer"}
        )
