from typing_extensions import Protocol

from billing.domain.credits.entities import CreditGrant
from billing.domain.subscription.repositories import (
    SubscriptionRepository,
)


class EventPublisher(Protocol):
    def publish(self, event: object) -> None:
        raise NotImplementedError


class IdempotencyStore(Protocol):
    def get(self, key: str) -> str | None:
        raise NotImplementedError

    def save(self, key: str, fingerprint: str) -> None:
        raise NotImplementedError


class CreditGrantWriter(Protocol):
    def save(self, grant: CreditGrant) -> None:
        raise NotImplementedError


class SubscriptionApplicationUnitOfWork(Protocol):
    subscription: SubscriptionRepository
    credit_grant: CreditGrantWriter

    def commit(self) -> None:
        raise NotImplementedError

    def rollback(self) -> None:
        raise NotImplementedError
