from typing import Protocol

from billing.domain.credits.aggregates import CreditAccount
from billing.domain.shared.ids import UserId


class CreditAccountRepository(Protocol):
    async def get(
        self, account_id: CreditAccountId
    ) -> CreditAccount | None: ...

    async def get_by_user_id(
        self, user_id: UserId
    ) -> CreditAccount | None: ...

    async def save(
        self, account: CreditAccount
    ) -> None: ...


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
