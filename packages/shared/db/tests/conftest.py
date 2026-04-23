from collections.abc import AsyncIterator
import os

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from db.app_db.base import AppBase
from db.app_db.engine import create_app_engine
from db.app_db.session import create_app_session_factory
from db.config.settings import AppDBSettings


@pytest.fixture(scope="session")
def app_db_settings() -> AppDBSettings:
    return AppDBSettings(
        url=os.getenv("TEST_APP_DB_URL", "sqlite+aiosqlite:///:memory:"),
    )


@pytest_asyncio.fixture(scope="session")
async def app_engine(app_db_settings: AppDBSettings) -> AsyncIterator[AsyncEngine]:
    engine = create_app_engine(app_db_settings)

    async with engine.begin() as conn:
        await conn.run_sync(AppBase.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def app_session(app_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    session_factory = create_app_session_factory(app_engine)

    async with session_factory() as session:
        yield session

        await session.rollback()
