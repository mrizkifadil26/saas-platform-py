from decimal import Decimal

from billing.domain.credits.value_objects import Credits
from billing.domain.payg.value_objects import Money
from billing.domain.pricing.entities import SubscriptionPlan
from billing.domain.shared.enums import BillingInterval
from billing.domain.shared.value_objects import PlanCode
from billing.domain.subscription.exceptions import (
    UnknownPlan,
)

CATALOG: dict[str, SubscriptionPlan] = {
    "sub_basic_monthly": SubscriptionPlan(
        code=PlanCode("sub_basic_monthly"),
        name="Basic Monthly",
        interval=BillingInterval.MONTH,
        included_credits=Credits(1000),
        price=Money(
            amount=Decimal("99.00"), currency="USD"
        ),
    ),
    "sub_pro_monthly": SubscriptionPlan(
        code=PlanCode("sub_pro_monthly"),
        name="Pro Monthly",
        interval=BillingInterval.MONTH,
        included_credits=Credits(5000),
        price=Money(
            amount=Decimal("299.00"), currency="USD"
        ),
    ),
    "sub_enterprise_monthly": SubscriptionPlan(
        code=PlanCode("sub_enterprise_monthly"),
        name="Enterprise Monthly",
        interval=BillingInterval.MONTH,
        included_credits=Credits(20000),
        price=Money(
            amount=Decimal("999.00"), currency="USD"
        ),
    ),
}


def get_subscription_plan(
    code: PlanCode,
) -> SubscriptionPlan:
    p = CATALOG.get(str(code))
    if not p:
        raise UnknownPlan(str(code))

    return p
