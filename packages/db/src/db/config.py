from pydantic_settings import BaseSettings

from .base import Base
from .session import SessionLocal, engine


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/app"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
