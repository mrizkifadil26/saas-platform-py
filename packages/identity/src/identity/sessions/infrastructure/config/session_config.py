from pydantic_settings import BaseSettings


class SessionSettings(BaseSettings):
    access_token_lifetime_minutes: int = 15
    refresh_token_lifetime_days: int = 15

    class Config:
        env_prefix = "SESSION_"
