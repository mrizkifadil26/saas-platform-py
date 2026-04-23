from __future__ import annotations

from dataclasses import dataclass

from billing.domain.value_objects.base_id import BaseId


@dataclass(frozen=True, slots=True)
class SubscriptionId(BaseId):
    """Value object representing a subscription ID."""

    pass
