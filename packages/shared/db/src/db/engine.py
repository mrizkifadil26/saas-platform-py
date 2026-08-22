from packages.shared.db.src.db.settings import BaseDBSettings
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
)


def create_engine(cfg: BaseDBSettings) -> AsyncEngine:
    return create_async_engine(
        cfg.url,
        pool_pre_ping=True,
        pool_size=cfg.pool_size,
        max_overflow=cfg.max_overflow,
        pool_timeout=cfg.pool_timeout,
        pool_recycle=cfg.pool_recycle,
    )
