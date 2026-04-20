from dataclasses import dataclass

from billing.domain.credits.value_objects import Credits
from billing.domain.payg.exceptions import UnknownPaygPack
from billing.domain.shared.value_objects import PlanCode


@dataclass(frozen=True)
class PaygPack:
    code: PlanCode
    credits: Credits
    price_cents: int
    currency: str = "usd"


CATALOG: dict[str, PaygPack] = {
    "payg_10_usd": PaygPack(
        code=PlanCode("payg_10_usd"),
        credits=Credits(100),
        price_cents=1000,
    ),
    "payg_50_usd": PaygPack(
        code=PlanCode("payg_50_usd"),
        credits=Credits(600),
        price_cents=5000,
    ),
    "payg_100_usd": PaygPack(
        code=PlanCode("payg_100_usd"),
        credits=Credits(1300),
        price_cents=10000,
    ),
    "payg_500_usd": PaygPack(
        code=PlanCode("payg_500_usd"),
        credits=Credits(7500),
        price_cents=50000,
    ),
    "payg_1000_usd": PaygPack(
        code=PlanCode("payg_1000_usd"),
        credits=Credits(17000),
        price_cents=100000,
    ),
}


def get_payg_pack(code: PlanCode) -> PaygPack:
    p = CATALOG.get(str(code))
    if not p:
        raise UnknownPaygPack(str(code))

    return p
