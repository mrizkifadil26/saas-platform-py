from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from iam.accounts.domain.value_objects import UserId
from iam.registration.domain import (
    Registration,
    RegistrationMethod,
    RegistrationStatus,
    RegistrationStep,
)
from iam.registration.domain.value_objects import EmailChallengeId, RegistrationId, ResumeToken
from iam.shared.domain.email import EmailAddress


@dataclass(frozen=True, slots=True)
class RegistrationView:
    registration_id: RegistrationId
    status: RegistrationStatus
    method: RegistrationMethod
    step: RegistrationStep

    email: EmailAddress | None
    email_verified: bool

    password_configured: bool
    display_name: str | None

    expires_at: datetime

    @classmethod
    def from_result(
        cls,
        result: Registration,
    ) -> RegistrationView:
        return RegistrationView(
            registration_id=result.id,
            status=result.status,
            method=result.method,
            step=result.step,
            email=result.email,
            email_verified=result.email_verified_at is not None,
            password_configured=result.password_hash is not None,
            display_name="",
            expires_at=result.expires_at,
        )


@dataclass(frozen=True, slots=True)
class RegistrationStarted:
    registration_id: RegistrationId
    method: RegistrationMethod
    step: RegistrationStep

    expires_at: datetime
    resume_token: ResumeToken | None


@dataclass(frozen=True, slots=True)
class EmailVerificationResult:
    registration: RegistrationView
    resend_after: timedelta | None = None


@dataclass(frozen=True, slots=True)
class PasswordSet:
    registration: RegistrationView


@dataclass(frozen=True, slots=True)
class RegistrationCompleted:
    user_id: UserId


@dataclass(frozen=True, slots=True)
class RegistrationCancelled:
    registration: RegistrationView


@dataclass(frozen=True, slots=True)
class VerifiedOIDCIdentity:
    """Construct only from a validated server-side OIDC callback."""

    issuer: str
    subject: str
    email: str
    display_name: str | None = None


@dataclass(frozen=True, slots=True)
class SendEmailVerification:
    registration_id: RegistrationId
    challenge_id: EmailChallengeId
    email: EmailAddress
    token: str
