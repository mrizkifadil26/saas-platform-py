from collections.abc import AsyncGenerator
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


def get_app_users_sessionmaker(request: Request) -> async_sessionmaker[AsyncSession]:
    return request.app.state.app_users_sessionmaker


async def get_app_users_session(
    sessionmaker: async_sessionmaker[AsyncSession] = Depends(get_app_users_sessionmaker),
) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        try:
            yield session
            await session.commit()

        except Exception:
            await session.rollback()
            raise
