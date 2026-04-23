from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BaseDBSettings:
    db_url: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 1800

    def __post_init__(self) -> None:
        if not self.db_url:
            raise ValueError("Database URL cannot be empty")


@dataclass(frozen=True, slots=True)
class AppDBSettings(BaseDBSettings):
    pass


@dataclass(frozen=True, slots=True)
class ProductDBSettings(BaseDBSettings):
    pass
