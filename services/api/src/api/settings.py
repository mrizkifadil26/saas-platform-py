from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from api.http.settings import HTTPSettings
from db import AppDBSettings
from identity.shared.infrastructure.cache.redis.settings import RedisSettings
from identity.shared.infrastructure.messaging.rabbitmq.settings import RabbitMQSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        env_nested_delimiter="__",
        extra="ignore",
        frozen=True,
    )

    app_name: str = "SaaS Platform API"
    environment: str = "dev"
    app_version: str = "0.1.0"
    debug: bool = False

    # security: SecuritySettings = SecuritySettings()

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

    http: HTTPSettings = Field(default_factory=lambda: HTTPSettings())

    access_token_ttl_seconds: int = 900
    refresh_token_ttl_seconds: int = 60 * 60 * 24 * 30

    database_pool_size: int = 10
    database_max_overflow: int = 20

    shutdown_timeout_seconds: float = 30.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
