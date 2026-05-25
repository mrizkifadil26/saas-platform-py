from datetime import datetime, timedelta

from iam.identity.domain import EmailVerification, User, UserStatus
from iam.identity.domain.value_objects import (
    Email,
    EmailVerificationId,
    EmailVerificationToken,
    EmailVerificationTokenHash,
    UserId,
)
from tests.factories.shared import make_datetime


def make_user_id(
    value: str | None = None,
) -> UserId:
    return UserId.from_string(value) if value is not None else UserId.generate()


def make_email(
    value: str = "test@example.com",
) -> Email:
    return Email(value)


def make_email_verification_token(
    value: str = "verification-token",
) -> EmailVerificationToken:
    return EmailVerificationToken(value)


def make_email_verification_token_hash(
    value: str = "hashed-verification-token",
) -> EmailVerificationTokenHash:
    return EmailVerificationTokenHash(value)


def make_user(
    *,
    id: UserId | None = None,
    email: Email | None = None,
    status: UserStatus = UserStatus.ACTIVE,
    created_at: datetime | None = None,
) -> User:
    return User(
        id=id or make_user_id(),
        email=email or make_email(),
        status=status,
        created_at=created_at or make_datetime(),
    )


def make_email_verification(
    *,
    user_id: UserId | None = None,
    token_hash: EmailVerificationTokenHash | None = None,
    created_at: datetime | None = None,
    expires_at: datetime | None = None,
    verified_at: datetime | None = None,
) -> EmailVerification:
    created_at = created_at or make_datetime()

    return EmailVerification(
        id=EmailVerificationId.generate(),
        user_id=user_id or make_user_id(),
        token_hash=token_hash or make_email_verification_token_hash(),
        created_at=created_at,
        expires_at=expires_at or created_at + timedelta(minutes=15),
        verified_at=verified_at,
    )
