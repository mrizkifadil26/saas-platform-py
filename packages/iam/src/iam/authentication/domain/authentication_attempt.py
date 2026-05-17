from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from iam.identity.domain.value_objects import EmailAddress, UserId
from iam.shared.domain import AggregateRoot

from .enums import AuthenticationStatus
from .value_objects import AuthenticationAttemptId


@dataclass(slots=True)
class AuthenticationAttempt(AggregateRoot[AuthenticationAttemptId]):
    email: EmailAddress
    user_id: UserId | None

    ip_address: str | None
    user_agent: str | None

    status: AuthenticationStatus

    failure_reason: str | None
    attempted_at: datetime

    locked_out_until: datetime | None = None

    @classmethod
    def create(
        cls,
        *,
        email: EmailAddress,
        ip_address: str | None,
        user_agent: str | None,
        attempted_at: datetime,
    ) -> AuthenticationAttempt:
        return cls(
            id=AuthenticationAttemptId.generate(),
            email=email,
            user_id=None,
            ip_address=ip_address,
            user_agent=user_agent,
            status=AuthenticationStatus.PENDING,
            failure_reason=None,
            attempted_at=attempted_at,
        )

    @property
    def is_pending(self) -> bool:
        return self.status == AuthenticationStatus.PENDING

    @property
    def is_successful(self) -> bool:
        return self.status == AuthenticationStatus.SUCCESS

    @property
    def is_failure(self) -> bool:
        return self.status == AuthenticationStatus.FAILURE

    @property
    def is_locked_out(self) -> bool:
        return (
            self.status == AuthenticationStatus.LOCKED_OUT
            and self.locked_out_until is not None
            and self.locked_out_until > datetime.now(UTC)
        )

    def mark_as_successful(
        self,
        *,
        user_id: UserId,
        # attempted_at: datetime,
    ) -> None:
        self.user_id = user_id
        self.status = AuthenticationStatus.SUCCESS
        self.failure_reason = None
        self.locked_out_until = None
        # self.attempted_at = attempted_at

        # TODO: record successful authentication attempt event

    def mark_as_failure(
        self,
        *,
        # attempted_at: datetime,
        failure_reason: str,
        user_id: UserId | None = None,
    ) -> None:
        self.user_id = user_id
        self.status = AuthenticationStatus.FAILURE
        self.failure_reason = failure_reason
        # self.attempted_at = attempted_at

        # TODO: record failed authentication attempt event

    def mark_as_locked_out(
        self,
        *,
        attempted_at: datetime,
        duration: timedelta,
    ) -> None:
        self.status = AuthenticationStatus.LOCKED_OUT
        self.locked_out_until = attempted_at + duration
        self.attempted_at = attempted_at

    def unlock(
        self,
        *,
        attempted_at: datetime,
    ) -> None:
        self.status = AuthenticationStatus.FAILURE
        self.locked_out_until = None
        self.attempted_at = attempted_at

    def can_retry(self) -> bool:
        return not self.is_locked_out

    def lock_remaining_seconds(
        self,
        *,
        now: datetime,
    ) -> int | None:
        if not self.is_locked_out or self.locked_out_until is None:
            return None

        remaining = (self.locked_out_until - now).total_seconds()
        return max(int(remaining), 0)
