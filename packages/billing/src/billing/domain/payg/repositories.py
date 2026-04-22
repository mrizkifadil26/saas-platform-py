from typing import Protocol

from billing.domain.payg.entities import PaygPurchase
from billing.domain.payg.value_objects import PaygPurchaseId


class PaygPurchaseRepository(Protocol):
    async def get(
        self, purchase_id: PaygPurchaseId
    ) -> PaygPurchase | None: ...

    async def save(
        self, purchase: PaygPurchase
    ) -> None: ...
