from dataclasses import dataclass

from billing.domain.value_objects.base_id import BaseId


@dataclass(frozen=True, slots=True)
class PlanId(BaseId):
    """Value object representing a subscription plan ID."""

    pass
