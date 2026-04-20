from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from collections.abc import AsyncIterator


async def get_app_users_session(sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncIterator:
    async with sessionmaker() as session:
        yield session
