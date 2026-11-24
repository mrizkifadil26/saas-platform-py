from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="IAM_",
        extra="ignore",
    )

    access_token_lifetime_seconds: int = 900
    refresh_token_lifetime_seconds: int = 2_592_000

    @property
    def access_token_lifetime(self) -> timedelta:
        return timedelta(
            seconds=self.access_token_lifetime_seconds,
        )

    @property
    def refresh_token_lifetime(self) -> timedelta:
        return timedelta(
            seconds=self.refresh_token_lifetime_seconds,
        )
