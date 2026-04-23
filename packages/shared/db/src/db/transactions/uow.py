from __future__ import annotations

from abc import ABC, abstractmethod


class AbstractUoW(ABC):
    async def __aenter__(self) -> AbstractUoW:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
