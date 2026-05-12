from typing import Protocol

from .user import User
from .value_objects import EmailAddress, UserId


class UserRepository(Protocol):
    async def save(self, user: User) -> None: ...

    async def find_by_id(self, user_id: UserId) -> User | None: ...

    async def find_by_email(self, email: EmailAddress) -> User | None: ...

    async def list(self, *, limit: int, offset: int) -> tuple[list[User], int]: ...
