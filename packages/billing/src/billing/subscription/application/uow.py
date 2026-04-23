from __future__ import annotations

from abc import ABC, abstractmethod

from billing.subscription.domain.subscription_repository import SubscriptionRepository


class SubscriptionUnitOfWork(ABC):
    subscriptions: SubscriptionRepository

    @abstractmethod
    async def __enter__(self) -> SubscriptionUnitOfWork:
        raise NotImplementedError

    @abstractmethod
    async def __exit__(self, exc_type, exc, tb) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
