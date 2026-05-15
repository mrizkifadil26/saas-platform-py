from datetime import datetime
from typing import Protocol

from iam.identity.domain.value_objects import UserId

from .authentication_attempt import AuthenticationAttempt


class AuthenticationAttemptRepository(Protocol):
    async def save(
        self,
        attempt: AuthenticationAttempt,
    ) -> None: ...

    async def find_recent_by_user_id(
        self,
        user_id: UserId,
        limit: int = 10,
    ) -> list[AuthenticationAttempt]: ...

    async def count_failures_since(
        self,
        user_id: UserId,
        since: datetime,
    ) -> int: ...
