from __future__ import annotations

from abc import abstractmethod

from db import AbstractUoW

from billing.subscription.domain.subscription_repository import SubscriptionRepository


class BillingUoW(AbstractUoW):
    @property
    @abstractmethod
    def subscriptions(self) -> SubscriptionRepository:
        raise NotImplementedError
