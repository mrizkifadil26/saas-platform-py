from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from db import AppDBSettings
from iam.shared.infrastructure.cache.redis.settings import RedisSettings
from iam.shared.infrastructure.messaging.rabbitmq.settings import RabbitMQSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        extra="ignore",
    )

    app_name: str = "SaaS Platform API"
    app_version: str = "0.1.0"
    debug: bool = False

    db: AppDBSettings = Field(
        default_factory=lambda: AppDBSettings(
            url="postgresql+asyncpg://postgres:postgres@localhost:5432/app",
        )
    )

    redis: RedisSettings = Field(
        default_factory=RedisSettings,
    )

    rabbitmq: RabbitMQSettings = Field(
        default_factory=RabbitMQSettings,
    )

    jwt_secret: str = Field(
        default=...,
        min_length=32,
    )

    jwt_algorithm: str = "HS256"

    access_token_ttl_seconds: int = 900
    refresh_token_ttl_seconds: int = 60 * 60 * 24 * 30

    database_pool_size: int = 10
    database_max_overflow: int = 20

    shutdown_timeout_seconds: float = 30.0

    cors_allow_origins: list[str] = ["http://localhost:3000"]
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    cors_allow_credentials: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
