from abc import ABC, abstractmethod

from billing.domain.shared.ids import UserId
from billing.domain.subscription.entities import (
    Subscription,
)
from billing.domain.subscription.value_objects import (
    SubscriptionId,
)


class SubscriptionRepository(ABC):
    @abstractmethod
    async def get(
        self, subscription_id: SubscriptionId
    ) -> Subscription | None:
        raise NotImplementedError

    @abstractmethod
    async def get_active_for_user(
        self, user_id: UserId
    ) -> Subscription | None:
        raise NotImplementedError

    @abstractmethod
    async def save(
        self, subscription: Subscription
    ) -> None:
        raise NotImplementedError
