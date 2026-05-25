from datetime import timedelta

import pytest

from iam.identity.domain import EmailVerification
from iam.identity.domain.exceptions import (
    EmailVerificationAlreadyVerifiedError,
    EmailVerificationExpiredError,
)
from tests.factories.identity import (
    make_email_verification,
    make_email_verification_token_hash,
    make_user_id,
)
from tests.factories.shared import make_datetime


class TestVerificationCreate:
    def test_create_generates_id(self) -> None:
        user_id = make_user_id()
        token_hash = make_email_verification_token_hash()
        created_at = make_datetime()

        verification = EmailVerification.create(
            user_id=user_id,
            token_hash=token_hash,
            created_at=created_at,
        )

        assert verification.id is not None

    def test_create_sets_fields(self) -> None:
        user_id = make_user_id()
        token_hash = make_email_verification_token_hash()
        created_at = make_datetime()

        verification = EmailVerification.create(
            user_id=user_id,
            token_hash=token_hash,
            created_at=created_at,
        )

        assert verification.user_id == user_id
        assert verification.token_hash == token_hash
        assert verification.created_at == created_at

    def test_create_sets_default_expiration_to_15_minutes(self) -> None:
        user_id = make_user_id()
        token_hash = make_email_verification_token_hash()
        created_at = make_datetime()

        verification = EmailVerification.create(
            user_id=user_id,
            token_hash=token_hash,
            created_at=created_at,
        )

        assert verification.expires_at == created_at + timedelta(minutes=15)

    def test_create_uses_custom_ttl_minutes(self) -> None:
        user_id = make_user_id()
        token_hash = make_email_verification_token_hash()
        created_at = make_datetime()

        verification = EmailVerification.create(
            user_id=user_id,
            token_hash=token_hash,
            created_at=created_at,
            ttl_minutes=30,
        )

        assert verification.expires_at == created_at + timedelta(minutes=30)

    def test_create_starts_as_unverified(self) -> None:
        user_id = make_user_id()
        token_hash = make_email_verification_token_hash()
        created_at = make_datetime()

        verification = EmailVerification.create(
            user_id=user_id,
            token_hash=token_hash,
            created_at=created_at,
        )

        assert verification.verified_at is None
        assert verification.is_verified is False


class TestEmailVerificationIsVerified:
    def test_returns_false_when_not_verified(self) -> None:
        verification = make_email_verification()

        assert verification.is_verified is False

    def test_returns_true_when_verified(self) -> None:
        verified_at = make_datetime()
        verification = make_email_verification()

        verification.verified_at = verified_at

        assert verification.is_verified is True


class TestEmailVerificationIsExpired:
    def test_returns_false_when_not_expired(self) -> None:
        now = make_datetime()
        verification = make_email_verification(
            expires_at=now + timedelta(minutes=1),
        )

        assert verification.is_expired(now) is False

    def test_returns_true_when_expired(self) -> None:
        now = make_datetime()
        verification = make_email_verification(
            expires_at=now - timedelta(minutes=1),
        )

        assert verification.is_expired(now) is True

    def test_returns_true_when_now_equals_expiration_time(self) -> None:
        now = make_datetime()
        verification = make_email_verification(
            expires_at=now,
        )

        assert verification.is_expired(now) is True


class TestEmailVerificationMarkVerified:
    def test_marks_verification_as_verified(self) -> None:
        verified_at = make_datetime()
        verification = make_email_verification(
            expires_at=verified_at + timedelta(minutes=1),
        )

        verification.mark_verified(
            verified_at=verified_at,
        )

        assert verification.verified_at == verified_at
        assert verification.is_verified is True

    def test_raises_when_already_verified(self) -> None:
        verified_at = make_datetime()
        verification = make_email_verification(
            verified_at=verified_at,
        )

        with pytest.raises(EmailVerificationAlreadyVerifiedError):
            verification.mark_verified(
                verified_at=verified_at,
            )

    def test_raises_when_verification_is_expired(self) -> None:
        verified_at = make_datetime()
        verification = make_email_verification(
            expires_at=verified_at - timedelta(minutes=1),
        )

        with pytest.raises(EmailVerificationExpiredError):
            verification.mark_verified(
                verified_at=verified_at,
            )
