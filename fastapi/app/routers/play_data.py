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

from app.models import *

from  app.configs import Configs
SECRET_KEY = Configs.SECRET_KEY
ALGORITHM = Configs.ALGORITHM

router = APIRouter(
    prefix="/playdata",
    tags=['Play Data']
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
async def create(request: pydantic_play_data_in,
                 user: pydantic_user = Depends(get_current_user)):
    obj = ""
    try:
        obj = await PlayData.filter(owner=user.id).first()
    except:
        pass

    if not obj:
        request = request.dict(exclude_unset=True)
        # print(request)

        obj = await PlayData.create(**request, owner=user)
        if obj:
            # request["block_use_count"] = request["block_use_count"] + 1
            # obj = await pydantic_play_data.from_tortoise_orm(obj)

            return {"status": "ok", "data": obj}
        else:
            return {"status": "error"}
    else:
        return {"status": "error",
                "message": "already exists"}


@router.get('/all')
async def read_all():
    response = await pydantic_play_data_out.from_queryset(PlayData.all())
    if response:
        return {"status": "ok", "data": response}
    else:
        return {
            "status": "error",
            "message": "not exists"
        }


@router.get('/id/{uuid}')
async def read(uuid: str,
               user: pydantic_user = Depends(get_current_user)):
    logined_user = await User.get(id=user.id)
    obj = await PlayData.filter(id=uuid).first()
    owner = obj.owner_id
    if owner == logined_user.id:

        response = await pydantic_play_data_out.from_queryset_single(PlayData.get(id=uuid))
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
                 request: pydantic_play_data_in,
                 user: pydantic_user = Depends(get_current_user)):
    try:
        obj = await PlayData.filter(id=uuid).first()
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
    obj = await PlayData.filter(id=uuid).first()
    owner = obj.owner_id
    logined_user = await User.get(email=user.email)

    if owner == logined_user.id:
        obj = await PlayData.filter(id=uuid).first().delete()
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
async def user_login(user: pydantic_user_in = Depends(get_current_user)):
    obj = await PlayData.get(owner=user.id).first()

    if obj:
        return {
            "status": "ok",
            "data": {obj
                     }
        }
    else:
        return {"status": "error",
                "message": "not exist"}
