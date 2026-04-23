from typing import Protocol

from billing.domain.credits.entities import CreditGrant
from billing.domain.subscription.subscription_repository import (
    SubscriptionRepository,
)


class CreditGrantWriter(Protocol):
    async def save(self, grant: CreditGrant) -> None:
        raise NotImplementedError


class SubscriptionApplicationUnitOfWork(Protocol):
    subscription: SubscriptionRepository
    credit_grant: CreditGrantWriter

    async def commit(self) -> None:
        raise NotImplementedError

    async def rollback(self) -> None:
        raise NotImplementedError
