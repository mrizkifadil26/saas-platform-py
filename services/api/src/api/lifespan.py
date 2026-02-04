from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from db.engine.app_users import make_app_users_engine, make_app_users_sessionmaker
from db.config.settings import AppUsersDBSettings

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = app.state.settings

    db_cfg = AppUsersDBSettings(
        database_url=settings.db_url,
    )

    engine: AsyncEngine = make_app_users_engine(db_cfg)
    sessionmaker: async_sessionmaker[AsyncSession] = make_app_users_sessionmaker(engine)

    app.state.app_users_engine = engine
    app.state.app_users_sessionmaker = sessionmaker

    try:
        yield
    finally:
        await engine.dispose()
