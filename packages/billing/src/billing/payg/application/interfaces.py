from abc import ABC, abstractmethod
from dataclasses import dataclass

from billing.credits.domain.value_objects.credits import Credits
from billing.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class PaygCreditPackage:
    code: str
    name: str
    credits: Credits
    price: Money


class PaygPricingCatalog(ABC):
    """
    Read-side pricing dependency.

    PAYG application asks pricing:
    'What does package X cost?'

    It does NOT trust frontend price. Ever.
    """

    @abstractmethod
    async def get_payg_package(self, package_code: str) -> PaygCreditPackage | None:
        raise NotImplementedError
