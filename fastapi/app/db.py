from beanie import init_beanie
# from motor import motor_asyncio

from .auth.models import User
from .configs import Configs
from fastapi import FastAPI

from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

# client = motor_asyncio.AsyncIOMotorClient(
#     Configs.DB_URL, uuidRepresentation="standard"
# )
# database = client[Configs.DB_DATABASE]

DATABASE_URL = f"postgres://{Configs.DB_USER}:{Configs.DB_PASSWORD}@{Configs.DB_HOST}:{Configs.DB_PORT}/{Configs.DB_DATABASE}"

async def on_startup(app: FastAPI) -> None:
    # Tortoise.init_models(["app.models.user", "app.models.group"], "models")
    register_tortoise(
        app,
        db_url=f"{DATABASE_URL}",
        modules={"models": ["app.models", "app.auth.models"]},
        generate_schemas=True,
        add_exception_handlers=True
    )

