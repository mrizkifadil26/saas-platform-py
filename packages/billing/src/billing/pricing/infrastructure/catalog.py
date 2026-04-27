from __future__ import annotations

from datetime import datetime

from billing.pricing.application.interfaces import PricingCatalog
from billing.pricing.domain.pricing_key import PricingKey
from billing.pricing.domain.pricing_rule import PricingRule
from billing.pricing.domain.pricing_rule_repository import PricingRuleRepository


class RepositoryPricingCatalog(PricingCatalog):
    def __init__(self, pricing_rules: PricingRuleRepository) -> None:
        self._pricing_rules = pricing_rules

    async def get_active_rule(
        self,
        pricing_key: PricingKey,
        *,
        at: datetime,
    ) -> PricingRule | None:
        return await self._pricing_rules.get_active_by_key(
            pricing_key,
            at=at,
        )
