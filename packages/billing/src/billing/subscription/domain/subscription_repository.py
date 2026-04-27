from abc import abstractmethod
from datetime import datetime

from billing.shared.domain.repository import Repository
from billing.shared.domain.value_objects.user_id import UserId
from billing.subscription.domain.subscription import Subscription
from billing.subscription.domain.value_objects.subscription_id import SubscriptionId


class SubscriptionRepository(
    Repository[Subscription, SubscriptionId],
):
    """
    Domain-specific repository for Subscription aggregate.

    Extends the generic Repository and adds
    query methods that are meaningful for the domain.
    """

    @abstractmethod
    async def find_active_by_user(
        self,
        user_id: UserId,
    ) -> Subscription | None:
        """Find the active subscription for a given user, if any."""
        raise NotImplementedError

    @abstractmethod
    async def find_due_for_renewal(
        self,
        now: datetime,
    ) -> list[Subscription]:
        """Find all subscriptions that are due for renewal."""
        raise NotImplementedError

    @abstractmethod
    async def find_canceling_subscriptions(
        self,
    ) -> list[Subscription]:
        """Find all subscriptions that are in the process of canceling."""
        raise NotImplementedError
