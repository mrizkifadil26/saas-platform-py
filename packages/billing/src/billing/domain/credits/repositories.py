from abc import ABC, abstractmethod

from billing.domain.credits.entities import (
    CreditConsumption,
    CreditGrant,
)
from billing.domain.credits.value_objects import (
    ConsumptionId,
    GrantId,
)
from billing.domain.shared.ids import RequestId, UserId


class CreditGrantRepository(ABC):
    @abstractmethod
    async def get(
        self,
        grant_id: GrantId,
    ) -> CreditGrant | None:
        raise NotImplementedError

    @abstractmethod
    async def list_active_for_user(
        self,
        user_id: UserId,
    ) -> list[CreditGrant]:
        raise NotImplementedError

    @abstractmethod
    async def save(
        self,
        grant: CreditGrant,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def save_many(
        self,
        grants: list[CreditGrant],
    ) -> None:
        raise NotImplementedError


class CreditConsumptionRepository(ABC):
    @abstractmethod
    async def get(
        self,
        consumption_id: ConsumptionId,
    ) -> CreditConsumption | None:
        raise NotImplementedError

    @abstractmethod
    async def save(
        self,
        consumption: CreditConsumption,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_request_id(
        self,
        user_id: UserId,
        request_id: RequestId,
    ) -> bool:
        raise NotImplementedError
