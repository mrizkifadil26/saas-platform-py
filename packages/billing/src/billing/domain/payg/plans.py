from dataclasses import dataclass

from billing.domain.errors import UnknownPlan
from billing.domain.types import Credits, PlanCode


@dataclass(frozen=True)
class PaygPlan:
    code: PlanCode
    tier: str
    credits_grant: Credits
    price_cents: int
    currency: str = "usd"


CATALOG: dict[str, PaygPlan] = {
    "payg_10_usd": PaygPlan(
        code=PlanCode("payg_10_usd"),
        tier="pack_10",
        credits_grant=Credits(100),
        price_cents=1000,
    ),
    "payg_50_usd": PaygPlan(
        code=PlanCode("payg_50_usd"),
        tier="pack_50",
        credits_grant=Credits(600),
        price_cents=5000,
    ),
    "payg_100_usd": PaygPlan(
        code=PlanCode("payg_100_usd"),
        tier="pack_100",
        credits_grant=Credits(1300),
        price_cents=10000,
    ),
    "payg_500_usd": PaygPlan(
        code=PlanCode("payg_500_usd"),
        tier="pack_500",
        credits_grant=Credits(7500),
        price_cents=50000,
    ),
    "payg_1000_usd": PaygPlan(
        code=PlanCode("payg_1000_usd"),
        tier="pack_1000",
        credits_grant=Credits(17000),
        price_cents=100000,
    ),
}


def get_payg_plan(code: PlanCode) -> PaygPlan:
    p = CATALOG.get(str(code))
    if not p:
        raise UnknownPlan(str(code))

    return p
