"""
STATIC and SECRET data
"""
from pydantic import BaseSettings

from functools import lru_cache


class Settings(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    USE_CREDENTIALS: bool
    VALIDATE_CERTS: bool
    SITE_URL: str
    SITE_NAME: str

    COOKIE_AUTHORIZATION_NAME: str
    COOKIE_DOMAIN: str

    CLIENT_ID: str
    CLIENT_SECRETS_JSON: str

    SWAP_TOKEN_ENDPOINT: str
    SUCCESS_ROUTE: str
    ERROR_ROUTE: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    PROTOCOL: str
    FULL_HOST_NAME: str
    PORT_NUMBER: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    '''return .env setting
    this founction just 1 time load data'''
    return Settings()
