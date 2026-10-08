from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from .engine import create_engine
from .session import create_session_factory
from .settings import BaseDBSettings


@dataclass(slots=True)
class Database:
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]

    @classmethod
    def create(cls, cfg: BaseDBSettings) -> Database:
        engine = create_engine(cfg)

        return cls(
            engine=engine,
            session_factory=create_session_factory(engine),
        )

    async def health(self) -> None:
        async with self._engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        await self.engine.dispose()
