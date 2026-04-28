from __future__ import annotations

from billing.pricing.application.dto import PricingRuleDTO, PricingSnapshotDTO
from billing.pricing.application.interfaces import PricingCatalog
from billing.pricing.application.queries import (
    CreatePricingSnapshotQuery,
    GetPricingRuleQuery,
)
from billing.pricing.domain.pricing_snapshot import PricingSnapshot
from billing.pricing.domain.value_objects.pricing_key import PricingKey
from billing.pricing.exceptions import PricingRuleNotFound


class GetPricingRuleHandler:
    def __init__(self, pricing_catalog: PricingCatalog) -> None:
        self._pricing_catalog = pricing_catalog

    async def handle(self, query: GetPricingRuleQuery) -> PricingRuleDTO:
        pricing_key = PricingKey(query.pricing_key)

        rule = await self._pricing_catalog.get_active_rule(
            pricing_key,
            at=query.at,
        )

        if rule is None:
            raise PricingRuleNotFound(
                f"No active pricing rule found for key: {query.pricing_key}"
            )

        return PricingRuleDTO(
            id=rule.id,
            pricing_key=str(rule.pricing_key),
            unit_amount=rule.price.amount,
            currency_code=rule.price.currency,
            billing_scheme=rule.billing_scheme.value,
            active_from=rule.active_from,
            active_until=rule.active_until,
        )


class CreatePricingSnapshotHandler:
    def __init__(self, pricing_catalog: PricingCatalog) -> None:
        self._pricing_catalog = pricing_catalog

    async def handle(self, query: CreatePricingSnapshotQuery) -> PricingSnapshotDTO:
        pricing_key = PricingKey(query.pricing_key)

        rule = await self._pricing_catalog.get_active_rule(
            pricing_key,
            at=query.at,
        )

        if rule is None:
            raise PricingRuleNotFound(
                f"No active pricing rule found for key: {query.pricing_key}"
            )

        snapshot = PricingSnapshot(
            pricing_rule_id=rule.id,
            pricing_key=rule.pricing_key,
            price=rule.price,
            billing_scheme=rule.billing_scheme,
            captured_at=query.at,
        )

        return PricingSnapshotDTO(
            pricing_rule_id=snapshot.pricing_rule_id,
            pricing_key=str(snapshot.pricing_key),
            unit_amount=snapshot.price.amount,
            currency_code=snapshot.price.currency,
            billing_scheme=snapshot.billing_scheme.value,
            captured_at=snapshot.captured_at,
        )
