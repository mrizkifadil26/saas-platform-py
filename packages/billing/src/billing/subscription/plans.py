from dataclasses import dataclass

from billing.errors import UnknownPlan
from billing.types import Credits, PlanCode


@dataclass(frozen=True)
class SubscriptionPlan:
    code: PlanCode
    tier: str
    billing_interval: str
    credits_grant: Credits
    price_cents: int
    currency: str = "usd"


CATALOG: dict[str, SubscriptionPlan] = {
    "sub_basic_monthly": SubscriptionPlan(
        code=PlanCode("sub_basic_monthly"),
        tier="basic",
        billing_interval="month",
        credits_grant=Credits(1000),
        price_cents=9900,
    ),
    "sub_pro_monthly": SubscriptionPlan(
        code=PlanCode("sub_pro_monthly"),
        tier="pro",
        billing_interval="month",
        credits_grant=Credits(5000),
        price_cents=29900,
    ),
    "sub_enterprise_monthly": SubscriptionPlan(
        code=PlanCode("sub_enterprise_monthly"),
        tier="enterprise",
        billing_interval="month",
        credits_grant=Credits(20000),
        price_cents=99900,
    ),
}


def get_subscription_plan(code: PlanCode) -> SubscriptionPlan:
    p = CATALOG.get(str(code))
    if not p:
        raise UnknownPlan(str(code))

    return p
