from billing.domain.credits.value_objects import (
    Credits,
    ProductCode,
)
from billing.domain.pricing.models import (
    PricingCatalog,
    UsagePriceRule,
)


def calculate_usage_cost(
    *,
    catalog: PricingCatalog,
    product_code: ProductCode,
    quantity: int,
    at,
) -> Credits:
    rule: UsagePriceRule = catalog.get_usage_rule(
        product_code, at
    )
    return rule.calculate_cost(quantity)
