import os
from functools import lru_cache
from typing import List

from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    DEBUG: bool = False

    APP_NAME: str = "The Endings"
    HTTPS: bool = False
    HOST: str = "localhost"

    GOOGLE_OAUTH2_CLIENT_ID: str
    GOOGLE_OAUTH2_CLIENT_SECRET_JSON: str
    GOOGLE_OAUTH2_CLIENT_SECRET: str

    SWAP_TOKEN_ENDPOINT: str
    SUCCESS_ROUTE: str
    ERROR_ROUTE: str

    PROTOCOL: str
    FULL_HOST_NAME: str
    PORT_NUMBER: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_DATABASE: str
    DB_URL: str

    ORIGINS: List[str] = Field(['http://localhost'], env='ORIGINS')
    ALLOWED_HOSTS: List[str] = Field(..., env='ALLOWED_HOSTS')

    GOOGLE_CLIENT_ID: str = None
    GOOGLE_CLIENT_SECRET: str = None
    GOOGLE_CALLBACK_URL: str = None

    GITHUB_CLIENT_ID: str = None
    GITHUB_CLIENT_SECRET: str = None
    GITHUB_CALLBACK_URL: str = None

    KAKAO_CLIENT_ID: str = None
    KAKAO_CLIENT_SECRET: str = None
    KAKAO_CALLBACK_URL: str = None

    NAVER_CLIENT_ID: str = None
    NAVER_CLIENT_SECRET: str = None
    NAVER_CALLBACK_URL: str = None


    MAIL_USERNAME : str = None
    MAIL_FROM : str = None
    MAIL_PASSWORD : str = None
    MAIL_PORT : str = None
    MAIL_SERVER : str = None
    MAIL_STARTTLS : str = None
    MAIL_SSL_TLS : str = None
    USE_CREDENTIALS : str = None
    VALIDATE_CERTS : str = None

    SECRET  : str = None
    SITE_URL : str = None
    SITE_NAME : str = None

    class Config:
        env_file = "app/.env"

    @property
    def URL(self) -> str:
        protocol = 'https' if self.HTTPS else 'http'
        return f'{protocol}://{self.HOST}'


Configs = Settings()

@lru_cache()
def get_settings():
    return Configs
