from db.repositories import SQLAlchemyRepository

from billing.credits.domain.credit_account import CreditAccount
from billing.credits.domain.credit_account_repository import CreditAccountRepository
from billing.credits.domain.value_objects.credit_account_id import CreditAccountId
from billing.credits.infrastructure.persistence.sqlalchemy.models import (
    CreditAccountModel,
)
from billing.credits.infrastructure.persistence.sqlalchemy.orm_mappers import (
    CreditAccountORMMapper,
)
from billing.shared.domain.value_objects.user_id import UserId
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class SQLCreditAccountRepository(
    SQLAlchemyRepository[CreditAccount, CreditAccountId, CreditAccountModel],
    CreditAccountRepository,
):
    @property
    def model_type(self) -> type[CreditAccountModel]:
        return CreditAccountModel

    def _to_domain(self, model: CreditAccountModel) -> CreditAccount:
        return CreditAccountORMMapper.from_model(model)

    def _to_model(self, entity: CreditAccount) -> CreditAccountModel:
        return CreditAccountORMMapper.to_model(entity)

    async def get_by_user_id(self, user_id: UserId) -> CreditAccount | None:
        stmt = (
            select(CreditAccountModel)
            .where(CreditAccountModel.user_id == str(user_id))
            .options(
                # Eager load grants and ledger entries
                selectinload(CreditAccountModel.grants),
                selectinload(CreditAccountModel.ledger_entries),
            )
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def get(self, entity_id: CreditAccountId) -> CreditAccount | None:
        stmt = (
            select(CreditAccountModel)
            .where(CreditAccountModel.id == str(entity_id))
            .options(
                # Eager load grants and ledger entries
                selectinload(CreditAccountModel.grants),
                selectinload(CreditAccountModel.ledger_entries),
            )
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def save(self, entity: CreditAccount) -> None:
        existing = await self._session.get(
            CreditAccountModel,
            str(entity.id),
            options=[
                # Eager load grants and ledger entries for update
                selectinload(CreditAccountModel.grants),
                selectinload(CreditAccountModel.ledger_entries),
            ],
        )

        if existing is None:
            model = self._to_model(entity)
            self._session.add(model)
            return

        # Update existing model
        CreditAccountORMMapper.update_model(existing, entity)
