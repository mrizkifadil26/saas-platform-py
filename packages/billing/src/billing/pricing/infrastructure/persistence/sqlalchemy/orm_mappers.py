from __future__ import annotations

from billing.pricing.domain.price import Price
from billing.pricing.domain.pricing_key import PricingKey
from billing.pricing.domain.pricing_rule import BillingScheme, PricingRule
from billing.pricing.infrastructure.persistence.sqlalchemy.models import (
    PricingRuleModel,
)
from billing.shared.domain.value_objects.currency import Currency


class PricingRuleORMMapper:
    @staticmethod
    def to_domain(model: PricingRuleModel) -> PricingRule:
        return PricingRule(
            id=model.id,
            pricing_key=PricingKey(model.pricing_key),
            price=Price(
                amount=model.amount,
                currency=Currency(model.currency),
            ),
            billing_scheme=BillingScheme(model.billing_scheme),
            active_from=model.active_from,
            active_until=model.active_until,
        )

    @staticmethod
    def to_model(rule: PricingRule) -> PricingRuleModel:
        return PricingRuleModel(
            id=rule.id,
            pricing_key=str(rule.pricing_key),
            amount=rule.price.amount,
            currency=rule.price.currency,
            billing_scheme=rule.billing_scheme.value,
            active_from=rule.active_from,
            active_until=rule.active_until,
        )
