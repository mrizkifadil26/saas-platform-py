import pytest

from iam.identity.domain.value_objects import EmailVerificationToken
from iam.shared.domain.exceptions import ValidationError


class TestEmailVerificationToken:
    def test_creates_with_valid_value(self) -> None:
        token = EmailVerificationToken(
            "verification-token",
        )

        assert token.value == "verification-token"

    def test_str_returns_value(self) -> None:
        token = EmailVerificationToken(
            "verification-token",
        )

        assert str(token) == "verification-token"

    def test_normalizes_whitespace(self) -> None:
        token = EmailVerificationToken(
            "  verification-token  ",
        )

        assert token.value == "verification-token"

    def test_raises_when_empty(self) -> None:
        with pytest.raises(
            ValidationError,
            match="Verification token cannot be empty",
        ):
            EmailVerificationToken("")

    def test_raises_when_whitespace_only(self) -> None:
        with pytest.raises(
            ValidationError,
            match="Verification token cannot be empty",
        ):
            EmailVerificationToken("   ")
