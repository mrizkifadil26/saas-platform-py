from typing import Protocol

from iam.identity.domain.user import User
from iam.identity.domain.value_objects.email_address import EmailAddress
from iam.identity.domain.value_objects.user_id import UserId


class UserRepository(Protocol):
    async def save(self, user: User) -> None: ...

    async def find_by_id(self, user_id: UserId) -> User | None: ...

    async def find_by_email(self, email: EmailAddress) -> User | None: ...

    async def list(self, *, limit: int, offset: int) -> tuple[list[User], int]: ...
