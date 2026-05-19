from __future__ import annotations

from dataclasses import dataclass

from .enums import AuthenticationDenialReason


@dataclass(frozen=True, slots=True)
class AuthenticationDecision:
    is_authenticated: bool
    denial_reason: AuthenticationDenialReason | None = None

    @property
    def is_denied(self) -> bool:
        return not self.is_authenticated

    @classmethod
    def allow(cls) -> AuthenticationDecision:
        return cls(
            is_authenticated=True,
            denial_reason=None,
        )

    @classmethod
    def deny(
        cls,
        reason: AuthenticationDenialReason,
    ) -> AuthenticationDecision:
        return cls(
            is_authenticated=False,
            denial_reason=reason,
        )
