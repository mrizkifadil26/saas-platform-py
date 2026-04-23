from typing import Protocol, Self

from billing.domain.credits.repositories import (
    CreditConsumptionRepository,
    CreditGrantRepository,
)


class CreditsApplicationUnitOfWork(Protocol):
    grant_repo: CreditGrantRepository
    consumption_repo: CreditConsumptionRepository

    async def __aenter__(self) -> Self:
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
