from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from billing.pricing.domain.value_objects.pricing_key import PricingKey
from billing.shared.domain.value_objects.money import Money


class BillingScheme(StrEnum):
    FLAT = "flat"
    PER_UNIT = "per_unit"


@dataclass(frozen=True, slots=True)
class PricingRule:
    id: UUID
    pricing_key: PricingKey
    price: Money
    billing_scheme: BillingScheme
    active_from: datetime
    active_until: datetime | None = None

    def __post_init__(self) -> None:
        if self.active_until is not None and self.active_until <= self.active_from:
            raise ValueError("active_until must be after active_from")

    def is_active_at(self, moment: datetime) -> bool:
        if moment < self.active_from:
            return False

        if self.active_until is not None and moment >= self.active_until:
            return False

        return True

    def calculate_price(self, quantity: int = 1) -> Money:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        if self.billing_scheme == BillingScheme.FLAT:
            return self.price

        if self.billing_scheme == BillingScheme.PER_UNIT:
            return self.price.multiply(quantity)

        raise ValueError(f"Unsupported billing scheme: {self.billing_scheme}")
