from __future__ import annotations

from db.uow.types import SupportsCommitRollback


class AsyncUnitOfWork:
    def __init__(self, session: SupportsCommitRollback) -> None:
        self.session = session

    async def __aenter__(self) -> AsyncUnitOfWork:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
