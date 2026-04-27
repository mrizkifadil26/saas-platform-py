from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from billing.pricing.domain.price import Price
from billing.pricing.domain.pricing_key import PricingKey
from billing.pricing.domain.pricing_rule import BillingScheme


@dataclass(frozen=True, slots=True)
class PricingSnapshot:
    pricing_rule_id: UUID
    pricing_key: PricingKey
    unit_price: Price
    billing_scheme: BillingScheme
    captured_at: datetime

    def calculate_price(self, quantity: int = 1) -> Price:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        if self.billing_scheme == BillingScheme.FLAT:
            return self.unit_price

        if self.billing_scheme == BillingScheme.PER_UNIT:
            return self.unit_price.multiply(quantity)

        raise ValueError(f"Unsupported billing scheme: {self.billing_scheme}")
