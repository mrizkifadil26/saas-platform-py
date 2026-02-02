import asyncio
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from collections.abc import AsyncGenerator
import pytest_asyncio
from sqlalchemy import NullPool, make_url
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from tests.factories import Factories, build_factories

# TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]


def _assert_safe_test_db(url: str) -> None:
    u = make_url(url)
    db = (u.database or "").lower()
    if not db.endswith("_test"):
        raise RuntimeError(f"Refusing to run tests on non-test DB: {db}")
    # add forbidden hosts if you want:
    # if (u.host or "").lower() in {"prod", "production"}: ...


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


@pytest.fixture(scope="session")
def event_loop():
    """Use a single asyncio event loop for the whole test session.

    Required when you have session-scoped async resources (e.g., SQLAlchemy async engine).
    """
    loop = asyncio.new_event_loop()
    try:
        yield loop
    finally:
        loop.close()


@pytest.fixture(scope="session", autouse=True)
def load_env() -> None:
    root = _repo_root()
    # Prefer .env.test for pytest; fallback to .env.local if you want
    load_dotenv(root / ".env.test", override=False)


@pytest.fixture(scope="session")
def test_db_url() -> str:
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        raise RuntimeError("TEST_DATABASE_URL is required")

    _assert_safe_test_db(url)
    return url


@pytest_asyncio.fixture(scope="session")
async def engine(test_db_url: str) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(
        test_db_url,
        # pool_pre_ping=True,
        poolclass=NullPool,
        future=True,
    )

    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def db_session(
    engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Outer transaction per test, bound to ONE connection.
    Any commit inside the test is still rolled back at the end.
    """
    async with engine.connect() as conn:
        outer = await conn.begin()

        SessionLocal = async_sessionmaker(
            bind=conn,
            expire_on_commit=False,
            autoflush=False,
        )

        s = SessionLocal()
        try:
            yield s
        finally:
            await s.close()
            await outer.rollback()


@pytest.fixture
def sessionmaker(engine: AsyncEngine):
    return async_sessionmaker(
        engine,
        expire_on_commit=False,
        autoflush=False,
    )


@pytest.fixture
def factories(db_session) -> Factories:
    # db_session is your existing AsyncSession fixture
    return build_factories(db_session)
