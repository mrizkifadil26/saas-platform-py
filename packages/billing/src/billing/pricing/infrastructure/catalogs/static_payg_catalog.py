from __future__ import annotations

from decimal import Decimal

from billing.credits.domain.value_objects.credits import Credits
from billing.payg.application.interfaces import PaygCreditPackage, PaygPricingCatalog
from billing.payg.domain.value_objects.pack_code import PackCode
from billing.pricing.domain.exceptions import PricingNotFound
from billing.shared.domain.value_objects.currency import Currency
from billing.shared.domain.value_objects.money import Money


class StaticPaygCatalog(PaygPricingCatalog):
    def __init__(self) -> None:
        self._packs: dict[PackCode, PaygCreditPackage] = {
            PackCode("payg_10_usd"): PaygCreditPackage(
                code=PackCode("payg_10_usd"),
                name="PAYG $10",
                credits=Credits(100),
                price=Money(amount=Decimal("10.00"), currency=Currency("USD")),
            ),
            PackCode("payg_50_usd"): PaygCreditPackage(
                code=PackCode("payg_50_usd"),
                name="PAYG $50",
                credits=Credits(600),
                price=Money(amount=Decimal("50.00"), currency=Currency("USD")),
            ),
            PackCode("payg_100_usd"): PaygCreditPackage(
                code=PackCode("payg_100_usd"),
                name="PAYG $100",
                credits=Credits(1300),
                price=Money(amount=Decimal("100.00"), currency=Currency("USD")),
            ),
            PackCode("payg_500_usd"): PaygCreditPackage(
                code=PackCode("payg_500_usd"),
                name="PAYG $500",
                credits=Credits(7500),
                price=Money(amount=Decimal("500.00"), currency=Currency("USD")),
            ),
            PackCode("payg_1000_usd"): PaygCreditPackage(
                code=PackCode("payg_1000_usd"),
                name="PAYG $1000",
                credits=Credits(17000),
                price=Money(amount=Decimal("1000.00"), currency=Currency("USD")),
            ),
        }

    async def get_payg_package(
        self, package_code: PackCode
    ) -> PaygCreditPackage | None:
        pack = self._packs.get(package_code)
        if not pack:
            raise PricingNotFound(f"PAYG pack with code {package_code} not found.")

        return PaygCreditPackage(
            code=pack.code,
            name=pack.name,
            credits=pack.credits,
            price=pack.price,
        )
