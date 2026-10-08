from typing import Protocol, Self

from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork(Protocol):
    @property
    def session(self) -> AsyncSession: ...

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None: ...

    async def commit(self): ...
    async def rollback(self): ...
