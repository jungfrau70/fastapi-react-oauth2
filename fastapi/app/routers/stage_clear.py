# response_classes
from fastapi import APIRouter, Depends, status, HTTPException
import jwt
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Depends, Request, HTTPException, status

from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)

# signals
from tortoise.signals import post_save
from typing import List, Optional, Type

# image upload
from fastapi import File, UploadFile
import secrets
from PIL import Image

from models import *

# from dotenv import dotenv_values
# config_credentials = dotenv_values(".env")

from common.config import get_settings
SECRET_KEY = get_settings().SECRET_KEY
ALGORITHM = get_settings().ALGORITHM


router = APIRouter(
    prefix="/clear",
    tags=['Stage Clear']
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM])
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


@router.post("/create")
async def create(request: pydantic_stage_clear_in,
                 user: pydantic_user = Depends(get_current_user)):
    # obj = ""
    # try:
    #     obj = await StageClear.filter(owner=user.id).first()
    # except:
    #     pass

    if True:
        request = request.dict(exclude_unset=True)
        print(request)

        if request:
            obj = await StageClear.create(**request, owner=user)
            # obj = await pydantic_play_data.from_tortoise_orm(obj)

            return {"status": "ok", "data": obj}
        else:
            return {"status": "error"}
    else:
        return {"status": "error",
                "message": "already exists"}


@router.get('/all')
async def read_all():
    response = await pydantic_stage_clear_out.from_queryset(StageClear.all())
    if response:
        return {"status": "ok", "data": response}
    else:
        return {
            "status": "error",
            "message": "not exists"
        }


@router.get('/id/{uuid}')
async def read_one(uuid: str,
                   user: pydantic_user = Depends(get_current_user)):
    obj = await StageClear.filter(owner=user.id).first()
    owner = obj.owner_id

    logined_user = await User.get(id=user.id)

    if owner == logined_user.id:
        response = await pydantic_stage_clear_out.from_queryset_single(StageClear.get(id=uuid))
        if response:
            return {"status": "ok", "data": response}
        else:
            return {"status": "error"}
    else:
        return {
            "status": "error",
            "message": "not permitted"
        }


@router.put('/id/{uuid}', status_code=status.HTTP_202_ACCEPTED)
async def update(uuid: str,
                 request: pydantic_stage_clear_in,
                 user: pydantic_user = Depends(get_current_user)):
    try:
        obj = await StageClear.filter(id=uuid).first()
        owner = obj.owner_id
    except Exception as e:
        return {
            "status": "error",
            "message": "not exists"
        }

    logined_user = await User.get(id=user.id)
    if owner == logined_user.id and str(obj.id) == uuid:
        request = request.dict(exclude_unset=True)
        response = await obj.update_from_dict(request)
        await response.save()

        if response:
            return {
                "status": "ok",
                "data": response
            }
        else:
            return {"status": "error"}
    else:
        return {
            "status": "error",
            "message": "not permitted"
        }


@router.delete('/id/{uuid}', status_code=status.HTTP_202_ACCEPTED)
async def delete(uuid: str,
                 user: pydantic_user = Depends(get_current_user)):
    try:
        obj = await StageClear.filter(id=uuid).first()
        owner = obj.owner_id
    except Exception as e:
        print(e)

    logined_user = await User.get(email=user.email)

    if owner == logined_user.id:
        obj = await StageClear.filter(id=uuid).first().delete()
        if obj:
            return {
                "status": "ok",
                "message": "deleted"
            }
        else:
            return {"status": "error"}
    else:
        return {
            "status": "error",
            "message": "not permitted"
        }


@router.post("/mine")
async def read_mine(user: pydantic_user_in = Depends(get_current_user)):
    # response = await StageClear.get(owner=user.id).first()
    response = await StageClear.filter(owner_id=user.id)

    if response:
        return {
            "status": "ok",
            "data": response
        }
    else:
        return {"status": "error",
                "message": "not exist"}
