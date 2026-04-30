from __future__ import annotations

from db.app_db.session import AppSessionFactory
from sqlalchemy.ext.asyncio import AsyncSession

from billing.credits.domain.credit_account_repository import CreditAccountRepository
from billing.credits.infrastructure.persistence.sqlalchemy.repositories import (
    SQLCreditAccountRepository,
)
from billing.invoice.domain.invoice_repository import InvoiceRepository
from billing.invoice.infrastructure.persistence.sqlalchemy.repositories import (
    SQLInvoiceRepository,
)
from billing.payg.domain.payg_purchase_repository import PaygPurchaseRepository
from billing.payg.infrastructure.sqlalchemy.repositories import (
    SQLPaygPurchaseRepository,
)
from billing.payment.domain.payment_repository import PaymentRepository
from billing.payment.infrastructure.persistence.sqlalchemy.repositories import (
    SQLPaymentRepository,
)
from billing.shared.application.uow import BillingUoW
from billing.subscription.domain.subscription_repository import SubscriptionRepository
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
        self._subscriptions: SubscriptionRepository | None = None
        self._credit_accounts: CreditAccountRepository | None = None
        self._invoices: InvoiceRepository | None = None
        self._payments: PaymentRepository | None = None
        self._payg_purchases: PaygPurchaseRepository | None = None

    @property
    def subscriptions(self) -> SubscriptionRepository:
        if self._subscriptions is None:
            raise RuntimeError("UoW has not been entered")

        return self._subscriptions

    @property
    def credit_accounts(self) -> CreditAccountRepository:
        if self._credit_accounts is None:
            raise RuntimeError("UoW has not been entered")

        return self._credit_accounts

    @property
    def invoices(self) -> InvoiceRepository:
        if self._invoices is None:
            raise RuntimeError("UoW has not been entered")

        return self._invoices

    @property
    def payments(self) -> PaymentRepository:
        if self._payments is None:
            raise RuntimeError("UoW has not been entered")

        return self._payments

    @property
    def payg_purchases(self) -> PaygPurchaseRepository:
        if self._payg_purchases is None:
            raise RuntimeError("UoW has not been entered")

        return self._payg_purchases

    async def __aenter__(self) -> SQLAlchemyBillingUoW:
        self._session = self._session_factory()
        self._subscriptions = SQLSubscriptionRepository(self._session)
        self._credit_accounts = SQLCreditAccountRepository(self._session)
        self._invoices = SQLInvoiceRepository(self._session)
        self._payments = SQLPaymentRepository(self._session)
        self._payg_purchases = SQLPaygPurchaseRepository(self._session)

        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        try:
            await super().__aexit__(exc_type, exc, tb)
        finally:
            if self._session is not None:
                await self._session.close()

    async def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("Session is not initialized")

        await self._session.commit()

    async def rollback(self) -> None:
        if self._session is None:
            raise RuntimeError("Session is not initialized")

        await self._session.rollback()
