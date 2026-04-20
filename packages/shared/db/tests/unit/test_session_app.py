import pytest
from db.config.settings import AppDBSettings
from db.engines.app import make_app_engine, make_app_sessionmaker
from db.sessions.app import get_app_session
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_app_session():
    cfg = AppDBSettings(database_url="sqlite+aiosqlite:///./test_app.db")
    engine = make_app_engine(cfg)
    sessionmaker = make_app_sessionmaker(engine)

    async for session in get_app_session(sessionmaker):
        assert isinstance(session, AsyncSession)
        break

    await engine.dispose()
