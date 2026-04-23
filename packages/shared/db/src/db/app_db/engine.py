from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
)

from db.config.settings import AppDBSettings


def create_app_engine(cfg: AppDBSettings) -> AsyncEngine:
    return create_async_engine(
        cfg.db_url,
        pool_pre_ping=True,
        pool_size=cfg.pool_size,
        max_overflow=cfg.max_overflow,
        pool_timeout=cfg.pool_timeout,
        pool_recycle=cfg.pool_recycle,
    )
