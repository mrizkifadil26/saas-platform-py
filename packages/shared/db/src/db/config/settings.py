from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BaseDBSettings:
    database_url: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 1800


@dataclass(frozen=True, slots=True)
class AppDBSettings(BaseDBSettings):
    pass


@dataclass(frozen=True, slots=True)
class ProductDBSettings(BaseDBSettings):
    pass
