from decimal import Decimal
from typing import NewType

from billing.credits.domain.value_objects.credits import Credits
from billing.pricing.domain.entities import SubscriptionPlan
from billing.shared.domain.enums import BillingInterval
from billing.shared.domain.value_objects.currency import Currency
from billing.shared.domain.value_objects.money import Money

PlanCode = NewType("PlanCode", str)

CATALOG: dict[PlanCode, SubscriptionPlan] = {
    PlanCode("sub_basic_monthly"): SubscriptionPlan(
        code=PlanCode("sub_basic_monthly"),
        name="Basic Monthly",
        interval=BillingInterval.MONTH,
        included_credits=Credits(1000),
        price=Money(amount=Decimal("99.00"), currency=Currency.USD),
    ),
    PlanCode("sub_pro_monthly"): SubscriptionPlan(
        code=PlanCode("sub_pro_monthly"),
        name="Pro Monthly",
        interval=BillingInterval.MONTH,
        included_credits=Credits(5000),
        price=Money(amount=Decimal("299.00"), currency=Currency.USD),
    ),
    PlanCode("sub_enterprise_monthly"): SubscriptionPlan(
        code=PlanCode("sub_enterprise_monthly"),
        name="Enterprise Monthly",
        interval=BillingInterval.MONTH,
        included_credits=Credits(20000),
        price=Money(amount=Decimal("999.00"), currency=Currency.USD),
    ),
}


def get_subscription_plan(
    code: PlanCode,
) -> SubscriptionPlan:
    p = CATALOG.get(code)
    if not p:
        # TODO: should we raise a domain-specific exception here?
        raise ValueError(str(code))

    return p
