from datetime import datetime

from billing.pricing.domain.value_objects.price import Price
from billing.pricing.domain.pricing_rule import PricingRule
from billing.pricing.domain.pricing_rule_repository import PricingRuleRepository
from billing.pricing.domain.pricing_snapshot import PricingSnapshot
from billing.pricing.domain.value_objects.pricing_key import PricingKey


class PricingPolicy:
    def __init__(
        self,
        pricing_rules: PricingRuleRepository,
    ) -> None:
        self._pricing_rules = pricing_rules

    async def resolve_pricing_rule(
        self,
        pricing_key: PricingKey,
        *,
        at: datetime,
    ) -> PricingRule:
        price_rule = await self._pricing_rules.get_active_by_key(pricing_key, at=at)
        if price_rule is None:
            raise ValueError(f"No active price rule found for key: {pricing_key}")

        return price_rule

    async def calculate_price(
        self,
        pricing_key: PricingKey,
        *,
        quantity: int,
        at: datetime,
    ) -> Price:
        pricing_rule = await self.resolve_pricing_rule(pricing_key, at=at)
        return pricing_rule.calculate_price(quantity)

    async def create_snapshot(
        self,
        pricing_key: PricingKey,
        *,
        at: datetime,
    ) -> PricingSnapshot:
        pricing_rule = await self.resolve_pricing_rule(pricing_key, at=at)
        return PricingSnapshot(
            pricing_rule_id=pricing_rule.id,
            pricing_key=pricing_rule.pricing_key,
            unit_price=pricing_rule.price,
            billing_scheme=pricing_rule.billing_scheme,
            captured_at=at,
        )
