from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Protocol

from iam.authentication.domain.value_objects import PasswordHash
from iam.identity.domain.value_objects.email import Email


class PasswordHasher(Protocol):
    def hash(
        self,
        plain_password: str,
    ) -> PasswordHash: ...


class CredentialVerifier(Protocol):
    def verify_password(
        self,
        *,
        password: str,
        password_hash: PasswordHash,
    ) -> bool: ...


@dataclass(frozen=True, slots=True)
class LoginThrottleDecision:
    allowed: bool
    retry_after: timedelta | None = None

    @classmethod
    def allow(cls) -> LoginThrottleDecision:
        return cls(
            allowed=True,
            retry_after=None,
        )

    @classmethod
    def deny(
        cls,
        retry_after: timedelta,
    ) -> LoginThrottleDecision:
        return cls(
            allowed=False,
            retry_after=retry_after,
        )


class LoginThrottle(Protocol):
    async def acquire(
        self,
        *,
        email: Email,
        ip_address: str,
    ) -> LoginThrottleDecision: ...

    async def record_failure(
        self,
        *,
        email: Email,
        ip_address: str,
    ) -> None: ...

    async def record_success(
        self,
        *,
        email: Email,
        ip_address: str,
    ) -> None: ...
