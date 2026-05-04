from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from billing.credits.domain.credit_account_repository import CreditAccountRepository
from billing.invoice.domain.invoice_repository import InvoiceRepository
from billing.payg.domain.payg_purchase_repository import PaygPurchaseRepository
from billing.payment.domain.payment_repository import PaymentRepository
from billing.subscription.domain.subscription_repository import SubscriptionRepository


class BillingUoW(ABC):
    subscriptions: SubscriptionRepository
    credit_accounts: CreditAccountRepository
    invoices: InvoiceRepository
    payments: PaymentRepository
    payg_purchases: PaygPurchaseRepository

    async def __aenter__(self) -> Self:
        return self

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
