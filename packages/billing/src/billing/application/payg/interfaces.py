from __future__ import annotations

from typing import Protocol

from billing.domain.credits.entities import CreditGrant
from billing.domain.payg.entities import PaygPurchase


class PaygPurchaseRepository(Protocol):
    async def save(
        self,
        purchase: PaygPurchase,
    ) -> None:
        raise NotImplementedError


class CreditGrantRepository(Protocol):
    async def save_grant(
        self,
        grant: CreditGrant,
    ) -> None:
        raise NotImplementedError


class PaygApplicationUnitOfWork(Protocol):
    payg_purchase: PaygPurchaseRepository
    ledger: CreditGrantRepository

    async def __aenter__(self) -> PaygApplicationUnitOfWork:
        raise NotImplementedError

    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:
        raise NotImplementedError

    async def commit(self) -> None:
        raise NotImplementedError

    async def rollback(self) -> None:
        raise NotImplementedError
