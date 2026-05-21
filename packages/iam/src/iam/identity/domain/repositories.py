from typing import Protocol

from .email_verification import EmailVerification
from .user import User
from .value_objects import (
    Email,
    EmailVerificationId,
    EmailVerificationTokenHash,
    UserId,
)


class UserRepository(Protocol):
    async def save(self, user: User) -> None: ...

    async def find_by_id(
        self,
        user_id: UserId,
    ) -> User | None: ...

    async def find_by_email(
        self,
        email: Email,
    ) -> User | None: ...

    async def list(
        self,
        *,
        limit: int,
        offset: int,
    ) -> tuple[list[User], int]: ...


class EmailVerificationRepository(Protocol):
    async def save(
        self,
        verification: EmailVerification,
    ) -> None: ...

    async def find_by_id(
        self, verification_id: EmailVerificationId
    ) -> EmailVerification | None: ...

    async def find_by_token_hash(
        self,
        token_hash: EmailVerificationTokenHash,
    ) -> EmailVerification | None: ...
