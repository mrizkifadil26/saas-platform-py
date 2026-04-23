from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession


from db.repositories.base import Repository

EntityT = TypeVar("EntityT")
IdT = TypeVar("IdT")
ModelT = TypeVar("ModelT")


class SQLAlchemyRepository(
    Repository[EntityT, IdT],
    ABC,
    Generic[EntityT, IdT, ModelT],
):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @property
    @abstractmethod
    def model_type(self) -> type[ModelT]:
        raise NotImplementedError

    @abstractmethod
    def _to_domain(self, model: ModelT) -> EntityT:
        raise NotImplementedError

    @abstractmethod
    def _to_model(self, entity: EntityT) -> ModelT:
        raise NotImplementedError

    async def get(self, entity_id: IdT) -> EntityT | None:
        model = await self._session.get(self.model_type, entity_id)
        if model is None:
            return None

        return self._to_domain(model)

    async def save(self, entity: EntityT) -> None:
        model = self._to_model(entity)
        merged = await self._session.merge(model)
        self._session.add(merged)

    async def delete(self, entity: EntityT) -> None:
        model = self._to_model(entity)
        merged = await self._session.merge(model)
        await self._session.delete(merged)
