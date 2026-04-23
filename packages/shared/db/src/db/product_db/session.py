from typing import TypeAlias

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

ProductSessionFactory: TypeAlias = async_sessionmaker[AsyncSession]


def create_product_session_factory(engine: AsyncEngine) -> ProductSessionFactory:
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


# async def get_app_session(
#     sessionmaker: async_sessionmaker[AsyncSession],
# ) -> AsyncIterator[AsyncSession]:
#     async with sessionmaker() as session:
#         yield session
