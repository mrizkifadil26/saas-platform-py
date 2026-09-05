from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork(Protocol):
    session: AsyncSession

    async def __aenter__(self): ...
    async def __aexit__(self, *args): ...  # type: ignore
    async def commit(self): ...
    async def rollback(self): ...
