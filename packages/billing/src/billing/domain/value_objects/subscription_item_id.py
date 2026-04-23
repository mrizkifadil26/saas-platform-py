from dataclasses import dataclass

from billing.domain.value_objects.base_id import BaseId


@dataclass(frozen=True, slots=True, order=True)
class SubscriptionItemId(BaseId):
    """Value object representing a subscription item ID."""

    pass
