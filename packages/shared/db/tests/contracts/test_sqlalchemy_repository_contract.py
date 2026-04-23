from dataclasses import dataclass

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.sqlalchemy import SQLAlchemyRepository
from tests.integration.testing_models import AppTestModel


@dataclass
class FakeEntity:
    id: int | None
    name: str


class FakeRepository(SQLAlchemyRepository[FakeEntity, int, AppTestModel]):
    @property
    def model_type(self) -> type[AppTestModel]:
        return AppTestModel

    def _to_domain(self, model: AppTestModel) -> FakeEntity:
        return FakeEntity(id=model.id, name=model.name)

    def _to_model(self, entity: FakeEntity) -> AppTestModel:
        model = AppTestModel(name=entity.name)
        if entity.id is not None:
            model.id = entity.id
        return model


@pytest.mark.asyncio
async def test_sqlalchemy_repository_contract_save_and_get(
    app_session: AsyncSession,
) -> None:
    repo = FakeRepository(app_session)

    entity = FakeEntity(id=None, name="contract-test")
    await repo.save(entity)
    await app_session.commit()

    found = await repo.get(1)

    assert found is not None
    assert found.name == "contract-test"
