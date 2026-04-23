from __future__ import annotations


from sqlalchemy.ext.asyncio import AsyncSession


class AppTransactionManager:
    # _sf: async_sessionmaker[AsyncSession]

    # db: Optional[AsyncSession] = field(default=None, init=False, repr=False)

    # async def __aenter__(self) -> AppUoW:
    #     self.db = self._sf()
    #     return self

    # async def __aexit__(self, exc_type, exc, tb) -> None:
    #     assert self.db is not None

    #     try:
    #         if exc_type is None:
    #             await self.db.commit()
    #         else:
    #             await self.db.rollback()
    #     finally:
    #         await self.db.close()

    # def _require_db(self) -> AsyncSession:
    #     if self._session is None:
    #         raise RuntimeError("AppUsersUoW used outside of 'async with'")

    #     return self._session

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __aenter__(self) -> AppTransactionManager:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

    @property
    def session(self) -> AsyncSession:
        return self._session

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
