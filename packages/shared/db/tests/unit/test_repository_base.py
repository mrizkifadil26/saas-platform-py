from __future__ import annotations

from dataclasses import dataclass

import pytest


@dataclass
class FakeModel:
    id: int
    name: str


@dataclass
class FakeEntity:
    id: int
    name: str


class FakeSession:
    def __init__(self) -> None:
        self.storage: dict[int, FakeModel] = {}
        self.deleted_ids: list[int] = []

    async def get(self, model_type: type[FakeModel], entity_id: int) -> FakeModel | None:
        return self.storage.get(entity_id)

    async def merge(self, model: FakeModel) -> FakeModel:
        return model

    def add(self, model: FakeModel) -> None:
        self.storage[model.id] = model

    async def delete(self, model: FakeModel) -> None:
        self.deleted_ids.append(model.id)
        self.storage.pop(model.id, None)


class FakeRepository:
    def __init__(self, session: FakeSession) -> None:
        self._session = session

    async def get(self, entity_id: int) -> FakeEntity | None:
        model = await self._session.get(FakeModel, entity_id)
        if model is None:
            return None
        return FakeEntity(id=model.id, name=model.name)

    async def save(self, entity: FakeEntity) -> None:
        model = FakeModel(id=entity.id, name=entity.name)
        merged = await self._session.merge(model)
        self._session.add(merged)

    async def delete(self, entity: FakeEntity) -> None:
        model = FakeModel(id=entity.id, name=entity.name)
        merged = await self._session.merge(model)
        await self._session.delete(merged)


@pytest.mark.asyncio
async def test_repository_save_and_get() -> None:
    session = FakeSession()
    repo = FakeRepository(session)

    await repo.save(FakeEntity(id=1, name="alpha"))

    found = await repo.get(1)

    assert found == FakeEntity(id=1, name="alpha")


@pytest.mark.asyncio
async def test_repository_delete() -> None:
    session = FakeSession()
    repo = FakeRepository(session)

    entity = FakeEntity(id=1, name="alpha")
    await repo.save(entity)
    await repo.delete(entity)

    found = await repo.get(1)

    assert found is None
    assert session.deleted_ids == [1]
