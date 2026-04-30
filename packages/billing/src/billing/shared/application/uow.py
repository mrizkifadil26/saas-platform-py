from __future__ import annotations

from abc import abstractmethod

from db import AbstractUoW

from billing.credits.domain.credit_account_repository import CreditAccountRepository
from billing.invoice.domain.invoice_repository import InvoiceRepository
from billing.payg.domain.payg_purchase_repository import PaygPurchaseRepository
from billing.payment.domain.payment_repository import PaymentRepository
from billing.subscription.domain.subscription_repository import SubscriptionRepository


class BillingUoW(AbstractUoW):
    @property
    @abstractmethod
    def subscriptions(self) -> SubscriptionRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def credit_accounts(self) -> CreditAccountRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def invoices(self) -> InvoiceRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def payments(self) -> PaymentRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def payg_purchases(self) -> PaygPurchaseRepository:
        raise NotImplementedError
