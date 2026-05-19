from pydantic_settings import BaseSettings


class JwtSettings(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"

    class Config:
        env_prefix = "JWT_"
