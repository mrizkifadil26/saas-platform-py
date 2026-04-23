from typing import Protocol

from billing.domain.credits.entities import (
    CreditConsumption,
    CreditGrant,
)
from billing.domain.credits.value_objects import GrantId
from billing.domain.shared.ids import UserId


class CreditGrantRepository(Protocol):
    async def get(
        self, grant_id: GrantId
    ) -> CreditGrant | None: ...
    async def save(self, grant: CreditGrant) -> None: ...
    async def list_for_user(
        self, user_id: UserId
    ) -> list[CreditGrant]: ...
    async def exists_by_reference(
        self, reference_id: str
    ) -> bool: ...


class CreditConsumptionRepository(Protocol):
    async def save(
        self, consumption: CreditConsumption
    ) -> None: ...
    async def exists_by_reference(
        self, reference_id: str
    ) -> bool: ...


# class CreditAccountRepository(Protocol):
#     async def get(
#         self, account_id: CreditAccountId
#     ) -> CreditAccount | None: ...

#     async def get_by_user_id(
#         self, user_id: UserId
#     ) -> CreditAccount | None: ...

#     async def save(
#         self, account: CreditAccount
#     ) -> None: ...


# class CreditConsumptionRepository(ABC):
#     @abstractmethod
#     async def get(
#         self,
#         consumption_id: ConsumptionId,
#     ) -> CreditConsumption | None:
#         raise NotImplementedError

#     @abstractmethod
#     async def save(
#         self,
#         consumption: CreditConsumption,
#     ) -> None:
#         raise NotImplementedError

#     @abstractmethod
#     async def exists_by_request_id(
#         self,
#         user_id: UserId,
#         request_id: RequestId,
#     ) -> bool:
#         raise NotImplementedError
