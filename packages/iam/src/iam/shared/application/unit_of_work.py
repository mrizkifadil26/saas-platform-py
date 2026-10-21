from typing import Protocol, Self

from iam.identity.application.ports import EmailVerificationRepository, UserRepository
from iam.shared.infrastructure.outbox.repository import OutboxRepository


class UnitOfWork(Protocol):
    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None: ...

    async def commit(self): ...
    async def rollback(self): ...


class IAMUnitOfWork(UnitOfWork, Protocol):
    @property
    def users(self) -> UserRepository: ...

    @property
    def email_verifications(self) -> EmailVerificationRepository: ...

    @property
    def outbox(self) -> OutboxRepository: ...


class IAMUnitOfWorkFactory(Protocol):
    def __call__(self) -> IAMUnitOfWork: ...
