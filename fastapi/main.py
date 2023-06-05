
import os
from app.auth import AuthRouters
from app.configs import Configs
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db import on_startup
from app.routers import auth, user, achievement, ar_view, product_purchase, level_purchase, play_data, stage_clear, user_profile

# Instantiate the Application
def create_app() -> FastAPI:
    app = FastAPI(title="Coding&Play Backend API")
    return app

app = create_app()

app.add_middleware(
    CORSMiddleware,
    allow_origins=Configs.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
   os.makedirs("app/static/images")
except FileExistsError:
   pass
app.mount("/static", StaticFiles(directory="./app/static"), name="static")

# routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(user_profile.router)
app.include_router(achievement.router)
app.include_router(ar_view.router)
app.include_router(product_purchase.router)
app.include_router(level_purchase.router)
app.include_router(play_data.router)
app.include_router(stage_clear.router)

# Start DB Connection on Startup
@app.on_event("startup")
async def startup_event():
    await on_startup(app)
