from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from iam.identity.domain.value_objects import UserId
from iam.shared.domain import AggregateRoot

from .enums import AuthenticationStatus
from .value_objects import AuthenticationAttemptId


@dataclass(slots=True)
class AuthenticationAttempt(AggregateRoot[AuthenticationAttemptId]):
    user_id: UserId

    status: AuthenticationStatus

    ip_address: str
    user_agent: str

    attempted_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    failure_reason: str | None = None
    locked_out_until: datetime | None = None

    @classmethod
    def create(
        cls,
        user_id: UserId,
        *,
        ip_address: str,
        user_agent: str,
        attempted_at: datetime | None = None,
    ) -> AuthenticationAttempt:
        return cls(
            id=AuthenticationAttemptId.generate(),
            user_id=user_id,
            status=AuthenticationStatus.PENDING,
            ip_address=ip_address,
            user_agent=user_agent,
            attempted_at=attempted_at or datetime.now(UTC),
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

    def mark_as_successful(self, *, attempted_at: datetime) -> None:
        self.status = AuthenticationStatus.SUCCESS
        self.failure_reason = None
        self.locked_out_until = None
        self.attempted_at = attempted_at

        # TODO: record successful authentication attempt event

    def mark_as_failure(
        self,
        *,
        attempted_at: datetime,
        failure_reason: str,
    ) -> None:
        self.status = AuthenticationStatus.FAILURE
        self.failure_reason = failure_reason
        self.attempted_at = attempted_at

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

    def lock_remaining_seconds(self, *, now: datetime) -> int | None:
        if not self.is_locked_out or self.locked_out_until is None:
            return None

        remaining = (self.locked_out_until - now).total_seconds()
        return max(int(remaining), 0)
