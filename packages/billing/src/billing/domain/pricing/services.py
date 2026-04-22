from datetime import datetime

from billing.domain.credits.value_objects import Credits
from billing.domain.pricing.entities import UsagePriceRule


def calculate_usage_cost(
    *,
    product_code: ProductCode,
    quantity: int,
    rules: list[UsagePriceRule],
    at: datetime,
) -> Credits:
    effective_rules = [
        rule
        for rule in rules
        if rule.product_code == product_code
        and rule.is_effective_at(at)
    ]
    if not effective_rules:
        raise DomainInvariantError(
            f"no pricing rule found for product {product_code.value}"
        )

    effective_rules.sort(
        key=lambda r: r.effective_from, reverse=True
    )
    return effective_rules[0].calculate_cost(quantity)
