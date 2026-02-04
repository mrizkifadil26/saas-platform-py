from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PX_", env_file=".env")

    env: str = "local"
    api_name: str = "px-api"
    api_version: str = "0.1.0"

    db_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/app_users"
    db_echo: bool = False
