from db.repositories import SQLAlchemyRepository
from sqlalchemy import select

from billing.payg.domain.payg_purchase import PaygPurchase
from billing.payg.domain.payg_purchase_repository import PaygPurchaseRepository
from billing.payg.domain.value_objects.payg_purchase_id import PaygPurchaseId
from billing.payg.infrastructure.sqlalchemy.models import PaygPurchaseModel
from billing.payg.infrastructure.sqlalchemy.orm_mappers import PaygPurchaseORMMapper


class SQLPaygPurchaseRepository(
    SQLAlchemyRepository[PaygPurchase, PaygPurchaseId, PaygPurchaseModel],
    PaygPurchaseRepository,
):
    async def get(self, entity_id: PaygPurchaseId) -> PaygPurchase | None:
        stmt = select(PaygPurchaseModel).where(PaygPurchaseModel.id == str(entity_id))

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def save(self, entity: PaygPurchase) -> None:
        existing = await self._session.get(
            PaygPurchaseModel,
            str(entity.id),
        )

        if existing is None:
            model = self._to_model(entity)
            self._session.add(model)
            return

        # Update existing model
        PaygPurchaseORMMapper.update_model(existing, entity)

    @property
    def model_type(self) -> type[PaygPurchaseModel]:
        return PaygPurchaseModel

    def _to_domain(self, model: PaygPurchaseModel) -> PaygPurchase:
        return PaygPurchaseORMMapper.from_model(model)

    def _to_model(self, entity: PaygPurchase) -> PaygPurchaseModel:
        return PaygPurchaseORMMapper.to_model(entity)
