from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class PasswordSettings(BaseSettings):
    min_length: int = 12
    max_length: int = 128


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SEC_",
        env_file=".env",
        extra="ignore",
    )

    jwt_secret: SecretStr = Field(min_length=32)
    token_hash_secret: SecretStr = Field(min_length=32)

    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "saas-api"
    jwt_audience: str = "saas-app"

    opaque_token_bytes: int = 32

    password: PasswordSettings = PasswordSettings()
