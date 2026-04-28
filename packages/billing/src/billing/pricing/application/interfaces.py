from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from billing.pricing.domain.pricing_rule import PricingRule
from billing.pricing.domain.value_objects.pricing_key import PricingKey


class PricingCatalog(ABC):
    @abstractmethod
    async def get_active_rule(
        self,
        pricing_key: PricingKey,
        *,
        at: datetime,
    ) -> PricingRule | None:
        raise NotImplementedError
