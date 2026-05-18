from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from .credential import Credential
from .enums import AuthenticationFailureReason
from .interfaces import PasswordHasher


@dataclass(frozen=True)
class Authenticator:
    password_hasher: PasswordHasher

    def authenticate_with_password(
        self,
        *,
        credential: Credential,
        password: str,
    ) -> AuthenticationDecision:
        # Rule validation

        is_valid_password = self.password_hasher.verify(
            plain_password=password,
            password_hash=credential.secret_hash.value,
        )

        if not is_valid_password:
            return AuthenticationDecision.failure(
                AuthenticationFailureReason.INVALID_CREDENTIALS,
            )

        return AuthenticationDecision.success()


@dataclass(frozen=True, slots=True)
class AuthenticationDecision:
    is_success: bool
    failure_reason: AuthenticationFailureReason | None = None

    @property
    def is_failure(self) -> bool:
        return not self.is_success

    @classmethod
    def success(cls) -> Self:
        return cls(
            is_success=True,
            failure_reason=None,
        )

    @classmethod
    def failure(
        cls,
        reason: AuthenticationFailureReason,
    ) -> Self:
        return cls(
            is_success=False,
            failure_reason=reason,
        )
