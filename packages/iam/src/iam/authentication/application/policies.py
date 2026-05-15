from datetime import datetime, timedelta

from iam.authentication.domain import (
    AuthenticationAttemptRepository,
)
from iam.identity.domain.value_objects import UserId


class LoginRateLimitPolicy:
    MAX_ATTEMPTS = 5
    TIME_WINDOW_MINUTES = 15

    def __init__(
        self,
        repository: AuthenticationAttemptRepository,
    ) -> None:
        self._repository = repository

    async def is_locked(
        self,
        user_id: UserId,
        *,
        now: datetime,
    ) -> bool:
        since = now - timedelta(
            minutes=self.TIME_WINDOW_MINUTES,
        )

        failures = await self._repository.count_failures_since(
            user_id=user_id,
            since=since,
        )

        return failures >= self.MAX_ATTEMPTS
