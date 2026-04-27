from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from billing.pricing.domain.pricing_key import PricingKey
from billing.pricing.domain.pricing_rule import PricingRule


class PricingCatalog(ABC):
    @abstractmethod
    async def get_active_rule(
        self,
        pricing_key: PricingKey,
        *,
        at: datetime,
    ) -> PricingRule | None:
        raise NotImplementedError
