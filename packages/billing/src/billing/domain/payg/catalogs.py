from decimal import Decimal

from billing.domain.config import PAYG_EXPIRY_DAYS
from billing.domain.credits.value_objects import Credits
from billing.domain.payg.exceptions import UnknownPaygPack
from billing.domain.payg.value_objects import (
    Money,
    PackCode,
)
from billing.domain.pricing.entities import PaygPack
from billing.domain.shared.value_objects import PlanCode

CATALOG: dict[str, PaygPack] = {
    "payg_10_usd": PaygPack(
        code=PackCode("payg_10_usd"),
        name="PAYG $10",
        credits=Credits(100),
        price=Money(amount=Decimal("10.00"), currency="USD"),
        expires_in_days=PAYG_EXPIRY_DAYS,
    ),
    "payg_50_usd": PaygPack(
        code=PackCode("payg_50_usd"),
        name="PAYG $50",
        credits=Credits(600),
        price=Money(amount=Decimal("50.00"), currency="USD"),
        expires_in_days=PAYG_EXPIRY_DAYS,
    ),
    "payg_100_usd": PaygPack(
        code=PackCode("payg_100_usd"),
        name="PAYG $100",
        credits=Credits(1300),
        price=Money(amount=Decimal("100.00"), currency="USD"),
        expires_in_days=PAYG_EXPIRY_DAYS,
    ),
    "payg_500_usd": PaygPack(
        code=PackCode("payg_500_usd"),
        name="PAYG $500",
        credits=Credits(7500),
        price=Money(amount=Decimal("500.00"), currency="USD"),
        expires_in_days=PAYG_EXPIRY_DAYS,
    ),
    "payg_1000_usd": PaygPack(
        code=PackCode("payg_1000_usd"),
        name="PAYG $1000",
        credits=Credits(17000),
        price=Money(amount=Decimal("1000.00"), currency="USD"),
        expires_in_days=PAYG_EXPIRY_DAYS,
    ),
}


def get_payg_pack(code: PlanCode) -> PaygPack:
    p = CATALOG.get(str(code))
    if not p:
        raise UnknownPaygPack(str(code))

    return p
