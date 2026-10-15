from typing import Protocol

from iam.identity.domain import EmailVerification, User
from iam.identity.domain.value_objects import (
    Email,
    EmailVerificationId,
    EmailVerificationToken,
    EmailVerificationTokenHash,
    UserId,
)


class EmailVerificationTokenGenerator(Protocol):
    def generate(self) -> EmailVerificationToken: ...


class EmailVerificationTokenHasher(Protocol):
    def hash(
        self,
        raw_token: EmailVerificationToken,
    ) -> EmailVerificationTokenHash: ...


class UserRepository(Protocol):
    async def add(self, user: User) -> None: ...

    async def update(self, user: User) -> None: ...

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
    async def add(
        self,
        verification: EmailVerification,
    ) -> None: ...

    async def update(
        self,
        verification: EmailVerification,
    ) -> None: ...

    async def find_by_id(
        self, verification_id: EmailVerificationId
    ) -> EmailVerification | None: ...

    async def find_by_user_id(
        self,
        user_id: UserId,
    ) -> EmailVerification | None: ...

    async def find_active_token_hash_for_update(
        self,
        token_hash: EmailVerificationTokenHash,
    ) -> EmailVerification | None: ...
