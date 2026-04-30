from __future__ import annotations

from decimal import Decimal

from billing.credits.domain.value_objects.credits import Credits
from billing.payg.application.interfaces import (
    PaygCreditPackage,
    PaygPricingCatalog,
)
from billing.shared.domain.value_objects.currency import Currency
from billing.shared.domain.value_objects.money import Money


class StaticPaygPricingCatalog(PaygPricingCatalog):
    def __init__(self) -> None:
        self._packages: dict[str, PaygCreditPackage] = {
            "credits_1000": PaygCreditPackage(
                code="credits_1000",
                name="1,000 Credits",
                credits=Credits(1000),
                price=Money(
                    amount=Decimal("5.00"),
                    currency=Currency("USD"),
                ),
            ),
            "credits_5000": PaygCreditPackage(
                code="credits_5000",
                name="5,000 Credits",
                credits=Credits(5000),
                price=Money(
                    amount=Decimal("20.00"),
                    currency=Currency("USD"),
                ),
            ),
            "credits_10000": PaygCreditPackage(
                code="credits_10000",
                name="10,000 Credits",
                credits=Credits(10000),
                price=Money(
                    amount=Decimal("35.00"),
                    currency=Currency("USD"),
                ),
            ),
        }

    async def get_payg_package(
        self,
        package_code: str,
    ) -> PaygCreditPackage | None:
        return self._packages.get(package_code)
