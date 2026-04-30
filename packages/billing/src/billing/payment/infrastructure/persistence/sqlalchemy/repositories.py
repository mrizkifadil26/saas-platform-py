from db.repositories import SQLAlchemyRepository

from billing.invoice.domain.value_objects.invoice_id import InvoiceId
from billing.payment.domain.payment import Payment
from billing.payment.domain.payment_repository import PaymentRepository
from billing.payment.domain.value_objects.payment_id import PaymentId
from billing.payment.infrastructure.persistence.sqlalchemy.models import PaymentModel
from billing.payment.infrastructure.persistence.sqlalchemy.orm_mappers import (
    PaymentORMMapper,
)
from billing.shared.domain.value_objects.user_id import UserId
from sqlalchemy import select


class SQLPaymentRepository(
    SQLAlchemyRepository[Payment, PaymentId, PaymentModel],
    PaymentRepository,
):
    async def get(self, entity_id: PaymentId) -> Payment | None:
        stmt = select(PaymentModel).where(PaymentModel.id == str(entity_id))

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def save(self, entity: Payment) -> None:
        existing = await self._session.get(
            PaymentModel,
            str(entity.id),
        )

        if existing is None:
            model = self._to_model(entity)
            self._session.add(model)
            return

        # Update existing model
        PaymentORMMapper.update_model(existing, entity)

    async def find_by_invoice_id(self, invoice_id: InvoiceId) -> list[Payment]:
        stmt = (
            select(PaymentModel)
            .where(PaymentModel.invoice_id == str(invoice_id))
            .order_by(PaymentModel.created_at.desc())
        )

        result = await self._session.execute(stmt)

        return [self._to_domain(model) for model in result.scalars().all()]

    async def find_by_user_id(self, user_id: UserId) -> list[Payment]:
        stmt = (
            select(PaymentModel)
            .where(PaymentModel.user_id == str(user_id))
            .order_by(PaymentModel.created_at.desc())
        )

        result = await self._session.execute(stmt)

        return [self._to_domain(model) for model in result.scalars().all()]

    @property
    def model_type(self) -> type[PaymentModel]:
        return PaymentModel

    def _to_domain(self, model: PaymentModel) -> Payment:
        return PaymentORMMapper.from_model(model)

    def _to_model(self, entity: Payment) -> PaymentModel:
        return PaymentORMMapper.to_model(entity)
