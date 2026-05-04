from __future__ import annotations

from types import TracebackType
from typing import Self

from db.app_db import AppDBTransactionManager, AppSessionFactory
from sqlalchemy.ext.asyncio import AsyncSession

from billing.credits.infrastructure.persistence.sqlalchemy.repositories import (
    SQLCreditAccountRepository,
)
from billing.invoice.infrastructure.persistence.sqlalchemy.repositories import (
    SQLInvoiceRepository,
)
from billing.payg.infrastructure.sqlalchemy.repositories import (
    SQLPaygPurchaseRepository,
)
from billing.payment.infrastructure.persistence.sqlalchemy.repositories import (
    SQLPaymentRepository,
)
from billing.shared.application.uow import BillingUoW
from billing.subscription.infrastructure.persistence.sqlalchemy.repositories.sql_subscription_repository import (
    SQLSubscriptionRepository,
)


class SQLAlchemyBillingUoW(BillingUoW):
    def __init__(
        self,
        session_factory: AppSessionFactory,
    ) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._tx: AppDBTransactionManager | None = None

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        self._tx = AppDBTransactionManager(self._session)

        await self._tx.__aenter__()

        self.subscriptions = SQLSubscriptionRepository(self._session)
        self.credit_accounts = SQLCreditAccountRepository(self._session)
        self.invoices = SQLInvoiceRepository(self._session)
        self.payments = SQLPaymentRepository(self._session)
        self.payg_purchases = SQLPaygPurchaseRepository(self._session)

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._tx is not None:
            await self._tx.__aexit__(exc_type, exc, tb)

        if self._session is not None:
            await self._session.close()

    async def commit(self) -> None:
        if self._tx is None:
            raise RuntimeError("Unit of work has not been entered")

        await self._tx.commit()

    async def rollback(self) -> None:
        if self._tx is None:
            raise RuntimeError("Unit of work has not been entered")

        await self._tx.rollback()
