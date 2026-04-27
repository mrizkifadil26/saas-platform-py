from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from billing.pricing.domain.pricing_key import PricingKey
from billing.pricing.domain.pricing_rule import PricingRule
from billing.shared.domain.repository import Repository


class PricingRuleRepository(
    Repository[PricingRule, PricingKey],
):
    @abstractmethod
    async def get_active_by_key(
        self,
        pricing_key: PricingKey,
        *,
        at: datetime,
    ) -> PricingRule | None:
        raise NotImplementedError
