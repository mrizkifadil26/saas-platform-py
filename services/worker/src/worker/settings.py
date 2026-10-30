from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="WORKER_",
        extra="ignore",
    )

    # queue: str = "default"
    # concurrency: int = 4
    # reserve_timeout: int = 5
    # ttr: int = 60
    # priority: int = 2**31
    # dead_letter_queue: str = "dead_letter"

    # @staticmethod
    # def from_env() -> WorkerSettings:
    #     return WorkerConfig(
    #         queue=os.getenv("WORKER_QUEUE", "default"),
    #         concurrency=int(os.getenv("WORKER_CONCURRENCY", "4")),
    #         reserve_timeout=int(os.getenv("WORKER_RESERVE_TIMEOUT", "5")),
    #         ttr=int(os.getenv("WORKER_TTR", "60")),
    #         priority=int(os.getenv("WORKER_PRIORITY", str(2**31))),
    #         dead_letter_queue=os.getenv("WORKER_DEAD_LETTER_QUEUE", "dead_letter"),
    #     )


@lru_cache
def get_settings() -> Settings:
    return Settings()
