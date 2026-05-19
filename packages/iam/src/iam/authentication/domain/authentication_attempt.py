from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from iam.identity.domain.value_objects import EmailAddress, UserId
from iam.shared.domain import Entity

from .enums import (
    AuthenticationDenialReason,
    AuthenticationOutcome,
)
from .value_objects import AuthenticationAttemptId


@dataclass(slots=True)
class AuthenticationAttempt(Entity[AuthenticationAttemptId]):
    email: EmailAddress
    user_id: UserId | None

    ip_address: str | None
    user_agent: str | None

    outcome: AuthenticationOutcome
    denial_reason: AuthenticationDenialReason | None

    attempted_at: datetime

    # locked_out_until: datetime | None = None

    def __post_init__(self):
        if (
            self.outcome == AuthenticationOutcome.SUCCESS
            and self.denial_reason is not None
        ):
            raise ValueError("Successful attempt cannot have failure reason.")

        if self.outcome == AuthenticationOutcome.DENIED and self.denial_reason is None:
            raise ValueError("Failed attempt must include failure reason.")

    @classmethod
    def succeeded(
        cls,
        *,
        email: EmailAddress,
        user_id: UserId,
        attempted_at: datetime,
        ip_address: str | None,
        user_agent: str | None,
    ) -> AuthenticationAttempt:
        return cls(
            id=AuthenticationAttemptId.generate(),
            email=email,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            outcome=AuthenticationOutcome.SUCCESS,
            denial_reason=None,
            attempted_at=attempted_at,
        )

    @classmethod
    def denied(
        cls,
        *,
        email: EmailAddress,
        denial_reason: AuthenticationDenialReason | None,
        attempted_at: datetime,
        user_id: UserId | None = None,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> AuthenticationAttempt:
        return cls(
            id=AuthenticationAttemptId.generate(),
            email=email,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            outcome=AuthenticationOutcome.DENIED,
            denial_reason=denial_reason,
            attempted_at=attempted_at,
        )

    @property
    def is_successful(self) -> bool:
        return self.outcome == AuthenticationOutcome.SUCCESS

    @property
    def is_denied(self) -> bool:
        return self.outcome == AuthenticationOutcome.DENIED

    # @property
    # def is_locked_out(self) -> bool:
    #     return (
    #         self.status == AuthenticationStatus.LOCKED_OUT
    #         and self.locked_out_until is not None
    #         and self.locked_out_until > datetime.now(UTC)
    #     )

    # def mark_as_locked_out(
    #     self,
    #     *,
    #     attempted_at: datetime,
    #     duration: timedelta,
    # ) -> None:
    #     self.status = AuthenticationStatus.LOCKED_OUT
    #     self.locked_out_until = attempted_at + duration
    #     self.attempted_at = attempted_at

    # def unlock(
    #     self,
    #     *,
    #     attempted_at: datetime,
    # ) -> None:
    #     self.status = AuthenticationStatus.FAILURE
    #     self.locked_out_until = None
    #     self.attempted_at = attempted_at

    # def can_retry(self) -> bool:
    #     return not self.is_locked_out

    # def lock_remaining_seconds(
    #     self,
    #     *,
    #     now: datetime,
    # ) -> int | None:
    #     if not self.is_locked_out or self.locked_out_until is None:
    #         return None

    #     remaining = (self.locked_out_until - now).total_seconds()
    #     return max(int(remaining), 0)
