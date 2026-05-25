import pytest

from iam.identity.domain.value_objects import (
    EmailVerificationTokenHash,
)
from iam.shared.domain.exceptions import ValidationError


class TestEmailVerificationTokenHash:
    def test_creates_with_valid_value(self) -> None:
        token = EmailVerificationTokenHash(
            "hashed-token",
        )

        assert token.value == "hashed-token"

    def test_str_returns_value(self) -> None:
        token = EmailVerificationTokenHash(
            "hashed-token",
        )

        assert str(token) == "hashed-token"

    def test_normalizes_whitespace(self) -> None:
        token = EmailVerificationTokenHash(
            "  hashed-token  ",
        )

        assert token.value == "hashed-token"

    def test_raises_when_empty(self) -> None:
        with pytest.raises(
            ValidationError,
            match="Verification token hash cannot be empty",
        ):
            EmailVerificationTokenHash("")

    def test_raises_when_whitespace_only(self) -> None:
        with pytest.raises(
            ValidationError,
            match="Verification token hash cannot be empty",
        ):
            EmailVerificationTokenHash("   ")
