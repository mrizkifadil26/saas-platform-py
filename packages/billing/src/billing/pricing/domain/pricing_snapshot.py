from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from billing.pricing.domain.pricing_rule import BillingScheme
from billing.pricing.domain.value_objects.pricing_key import PricingKey
from billing.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class PricingSnapshot:
    pricing_rule_id: UUID
    pricing_key: PricingKey
    price: Money
    billing_scheme: BillingScheme
    captured_at: datetime

    def calculate_price(self, quantity: int = 1) -> Money:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        if self.billing_scheme == BillingScheme.FLAT:
            return self.price

        if self.billing_scheme == BillingScheme.PER_UNIT:
            return self.price.multiply(quantity)

        raise ValueError(f"Unsupported billing scheme: {self.billing_scheme}")
