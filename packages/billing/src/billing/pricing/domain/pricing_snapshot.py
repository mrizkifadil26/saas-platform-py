from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from billing.payg.domain.value_objects import Money
from billing.pricing.domain.pricing_rule import BillingScheme
from billing.pricing.domain.value_objects.pricing_key import PricingKey


@dataclass(frozen=True, slots=True)
class PricingSnapshot:
    pricing_rule_id: UUID
    pricing_key: PricingKey
    unit_price: Money
    billing_scheme: BillingScheme
    captured_at: datetime

    def calculate_price(self, quantity: int = 1) -> Money:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        if self.billing_scheme == BillingScheme.FLAT:
            return self.unit_price

        if self.billing_scheme == BillingScheme.PER_UNIT:
            return self.unit_price * quantity

        raise ValueError(f"Unsupported billing scheme: {self.billing_scheme}")
