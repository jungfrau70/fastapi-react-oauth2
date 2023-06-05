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
SITE_URL = Configs.SITE_URL

router = APIRouter(
    prefix="/profile",
    tags=['User Profile']
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
async def create(request: pydantic_user_profile_in,
                 user: pydantic_user = Depends(get_current_user)):
    obj = ""
    try:
        obj = await UserProfile.filter(owner=user.id).first()
    except:
        pass

    if not obj:
        request = request.dict(exclude_unset=True)
        print(request)

        if request:
            obj = await UserProfile.create(**request, owner=user)
            # obj = await pydantic_play_data.from_tortoise_orm(obj)

            return {"status": "ok", "data": obj}
        else:
            return {"status": "error"}
    else:
        return {"status": "error",
                "message": "already exists"}


@router.get('/all')
async def read_all():
    response = await pydantic_user_profile_out.from_queryset(UserProfile.all())
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
    obj = await UserProfile.filter(owner=user.id).first()
    owner = obj.owner_id

    logined_user = await User.get(id=user.id)

    if owner == logined_user.id:
        response = await pydantic_user_profile_out.from_queryset_single(UserProfile.get(id=uuid))
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
                 request: pydantic_user_profile_in,
                 user: pydantic_user = Depends(get_current_user)):
    try:
        obj = await UserProfile.filter(id=uuid).first()
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
async def make_disabled(uuid: str,
                        request: pydantic_user_profile_in,
                        user: pydantic_user = Depends(get_current_user)):
    obj = await PlayData.filter(id=uuid).first()
    owner = obj.owner_id
    logined_user = await User.get(email=user.email)

    if owner == logined_user.id:
        request = request.dict(exclude_unset=True)
        block_use_count = obj.block_use_count
        request["block_use_count"] = block_use_count + 1
        response = await PlayData.update_or_create(**request, owner=user)
        # response = await pydantic_play_data_out. (PlayData.update_or_create(**request, owner = user))
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


@router.post("/uploadfile/profile")
async def crate_upload_file(file: UploadFile = File(...),
                            user: pydantic_user = Depends(get_current_user)):
    user_profile = await UserProfile.get(owner=user.id)

    if user_profile:

        FILEPATH = './static/images/'
        filename = file.filename

        # test.png >> [ 'test', 'png' ]
        extention = filename.split(".")[1]

        if extention not in ['png', 'jpg']:
            return {
                "status": "error",
                "detail": "File extention is not allowed"
            }
        # ae9dd2737bf952163c57.png
        token_name = secrets.token_hex(10) + "." + extention
        generated_name = FILEPATH + token_name
        file_content = await file.read()

        with open(generated_name, "wb") as file:
            file.write(file_content)

        # PILLOW
        img = Image.open(generated_name)
        img = img.resize(size=(200, 200))
        img.save(generated_name)

        file.close()

        user_profile.logo = token_name
        await user_profile.save()

        file_url = SITE_URL + generated_name[1:]
        return {
            "status": "ok",
            "filename": file_url
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated to perform this action",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/mine/{device_id}")
async def user_login(device_id: str,
                     user: pydantic_user_in = Depends(get_current_user)):
    user_profile_obj = await UserProfile.get(owner=user.id)

    if device_id == user_profile_obj.device_name:
        logo = user_profile_obj.logo  # asbdasdfpioasdf.png
        logo_path = f"{SITE_URL}/static/images/" + logo

        return {
            "status": "ok",
            "data1": {
                "username": user.username,
                "login_from": user_profile_obj.login_from,
                "login_country": user_profile_obj.login_country,
                "is_active": user_profile_obj.is_active,
                "login_time": user_profile_obj.last_login_time,
                "device_name": user_profile_obj.device_name,
                "device_id": user_profile_obj.device_id,
            },
        }
    else:
        return {"status": "error",
                "message": f"already logined with other device {user_profile_obj.device_id}"}


@router.post("/mine")
async def read_mine(user: pydantic_user_in = Depends(get_current_user)):
    # response = await StageClear.get(owner=user.id).first()
    response = await UserProfile.filter(owner_id=user.id)

    if response:
        return {
            "status": "ok",
            "data": response
        }
    else:
        return {"status": "error",
                "message": "not exist"}

    # try:
    #     try:
    #         product_purchase_obj = await ProductPurchase.get(owner=user.id)
    #         if product_purchase_obj:
    #             user_profile_obj = await UserProfile.get(owner=user.id)
    #             level_purchase_obj = await LevelPurchase.get(owner=user.id)
    #             stage_clear_obj = await StageClear.get(owner=user.id)
    #             return {
    #                 "status": "ok",
    #                 'id': user.id,
    #                 'email': user.email,
    #                 'user_profile': user_profile_obj,
    #                 'level_purchase': level_purchase_obj,
    #                 'stage_clear': stage_clear_obj,
    #                 'product_purchase': product_purchase_obj,
    #             }
    #     except:
    #         pass
    #     try:
    #         user_profile_obj = await UserProfile.get(owner=user.id)
    #         level_purchase_obj = await LevelPurchase.get(owner=user.id)
    #         stage_clear_obj = await StageClear.get(owner=user.id)
    #         return {
    #             "status": "ok",
    #             'id': user.id,
    #             'email': user.email,
    #             'user_profile': user_profile_obj,
    #             'level_purchase': level_purchase_obj,
    #             'stage_clear': stage_clear_obj,
    #         }
    #     except:
    #         pass
    # except Exception as e:
    #     return {
    #         "status": "error",
    #         "message": e
    #         }
