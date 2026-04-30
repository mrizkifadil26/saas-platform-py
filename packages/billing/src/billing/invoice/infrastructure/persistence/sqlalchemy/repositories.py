from db.repositories import SQLAlchemyRepository

from billing.invoice.domain.invoice import Invoice
from billing.invoice.domain.invoice_repository import InvoiceRepository
from billing.invoice.domain.invoice_status import InvoiceStatus
from billing.invoice.domain.value_objects.invoice_id import InvoiceId
from billing.invoice.infrastructure.persistence.sqlalchemy.models import InvoiceModel
from billing.invoice.infrastructure.persistence.sqlalchemy.orm_mappers import (
    InvoiceORMMapper,
)
from billing.shared.domain.value_objects.user_id import UserId
from sqlalchemy import select


class SQLInvoiceRepository(
    SQLAlchemyRepository[Invoice, InvoiceId, InvoiceModel],
    InvoiceRepository,
):
    async def get(self, entity_id: InvoiceId) -> Invoice | None:
        stmt = select(InvoiceModel).where(InvoiceModel.id == entity_id.value)

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def save(self, entity: Invoice) -> None:
        existing = await self._session.get(
            InvoiceModel,
            entity.id.value,
        )

        if existing is None:
            model = self._to_model(entity)
            self._session.add(model)
            return

        # Update existing model
        InvoiceORMMapper.update_model(existing, entity)

    async def list_by_user_id(self, user_id: UserId) -> list[Invoice]:
        stmt = (
            select(InvoiceModel)
            .where(InvoiceModel.user_id == user_id.value)
            .order_by(InvoiceModel.created_at.desc())
        )

        result = await self._session.execute(stmt)

        return [self._to_domain(model) for model in result.scalars().all()]

    async def list_open_by_user_id(self, user_id: UserId) -> list[Invoice]:
        stmt = (
            select(InvoiceModel)
            .where(InvoiceModel.user_id == user_id.value)
            .where(InvoiceModel.status == InvoiceStatus.OPEN.value)
            .order_by(InvoiceModel.created_at.desc())
        )

        result = await self._session.execute(stmt)

        return [self._to_domain(model) for model in result.scalars().all()]

    @property
    def model_type(self) -> type[InvoiceModel]:
        return InvoiceModel

    def _to_domain(self, model: InvoiceModel) -> Invoice:
        return InvoiceORMMapper.from_model(model)

    def _to_model(self, entity: Invoice) -> InvoiceModel:
        return InvoiceORMMapper.to_model(entity)
