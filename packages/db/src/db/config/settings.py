from dataclasses import dataclass


@dataclass
class AppUsersDBSettings:
    database_url: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 1800
