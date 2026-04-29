from __future__ import annotations

from decimal import Decimal

from billing.credits.domain.value_objects.credits import Credits
from billing.payg.config import PAYG_EXPIRY_DAYS
from billing.payg.domain.value_objects.pack_code import PackCode
from billing.pricing.domain._entities import PaygPack
from billing.shared.domain.value_objects.currency import Currency
from billing.shared.domain.value_objects.money import Money
from billing.subscription.domain.plans import PlanCode

CATALOG: dict[str, PaygPack] = {
    "payg_10_usd": PaygPack(
        code=PackCode("payg_10_usd"),
        name="PAYG $10",
        credits=Credits(100),
        price=Money(amount=Decimal("10.00"), currency=Currency("USD")),
        expires_in_days=PAYG_EXPIRY_DAYS,
    ),
    "payg_50_usd": PaygPack(
        code=PackCode("payg_50_usd"),
        name="PAYG $50",
        credits=Credits(600),
        price=Money(amount=Decimal("50.00"), currency=Currency("USD")),
        expires_in_days=PAYG_EXPIRY_DAYS,
    ),
    "payg_100_usd": PaygPack(
        code=PackCode("payg_100_usd"),
        name="PAYG $100",
        credits=Credits(1300),
        price=Money(amount=Decimal("100.00"), currency=Currency("USD")),
        expires_in_days=PAYG_EXPIRY_DAYS,
    ),
    "payg_500_usd": PaygPack(
        code=PackCode("payg_500_usd"),
        name="PAYG $500",
        credits=Credits(7500),
        price=Money(amount=Decimal("500.00"), currency=Currency("USD")),
        expires_in_days=PAYG_EXPIRY_DAYS,
    ),
    "payg_1000_usd": PaygPack(
        code=PackCode("payg_1000_usd"),
        name="PAYG $1000",
        credits=Credits(17000),
        price=Money(amount=Decimal("1000.00"), currency=Currency("USD")),
        expires_in_days=PAYG_EXPIRY_DAYS,
    ),
}


def get_payg_pack(code: PlanCode) -> PaygPack:
    p = CATALOG.get(str(code))
    if not p:
        raise ValueError(f"PAYG pack with code {code} not found.")

    return p
