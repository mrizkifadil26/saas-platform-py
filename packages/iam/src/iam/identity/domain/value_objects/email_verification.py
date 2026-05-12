from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime


@dataclass(frozen=True, slots=True)
class EmailVerification:
    verified_at: datetime | None = None
    verification_requested_at: datetime | None = None

    @property
    def is_verified(self) -> bool:
        return self.verified_at is not None

    @property
    def is_pending(self) -> bool:
        return self.verification_requested_at is not None and not self.is_verified

    def mark_requested(
        self,
        *,
        requested_at: datetime,
    ) -> EmailVerification:
        if self.is_verified:
            raise ValueError("Email already verified")

        return replace(
            self,
            verification_requested_at=requested_at,
        )

    def verify(
        self,
        *,
        verified_at: datetime,
    ) -> EmailVerification:
        if self.is_verified:
            raise ValueError("Email already verified")

        return replace(
            self,
            verified_at=verified_at,
        )

    def reset_verification(self) -> EmailVerification:
        return replace(self)
