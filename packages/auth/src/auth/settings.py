from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AUTH_",
        extra="ignore",
    )

    JWT_ISSUER: str = ""
    JWT_AUDIENCE: str = ""
    JWT_SECRET: str
    JWT_ALG: str = "HS256"

    # TTLs
    ACCESS_TOKEN_TTL_MINUTES: int = 15
    REFRESH_TOKEN_TTL_DAYS: int = 30

    # Refresh rotation
    ROTATE_REFRESH_TOKENS: bool = True
