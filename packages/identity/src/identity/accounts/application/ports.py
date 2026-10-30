from typing import Protocol

from identity.accounts.domain.user import User
from identity.accounts.domain.value_objects import UserId
from identity.shared.domain.email import EmailAddress


class UserRepository(Protocol):
    async def add(self, user: User) -> None: ...

    async def update(self, user: User) -> None: ...

    async def find_by_id(
        self,
        user_id: UserId,
    ) -> User | None: ...

    async def find_by_email(
        self,
        email: EmailAddress,
    ) -> User | None: ...

    async def list(
        self,
        *,
        limit: int,
        offset: int,
    ) -> tuple[list[User], int]: ...
