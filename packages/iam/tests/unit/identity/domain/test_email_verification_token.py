
from tests.contracts.domain.string_value_object import (
    assert_rejects_empty,
    assert_trims_whitespace,
    assert_valid_string_value_object,
)

from iam.identity.domain.value_objects import EmailVerificationToken
from iam.shared.kernel.exceptions import ValidationError


class TestEmailVerificationToken:
    def test_string_value_object_contract(self) -> None:
        assert_valid_string_value_object(
            EmailVerificationToken,
            "verification-token",
        )

        assert_trims_whitespace(
            EmailVerificationToken,
            "verification-token",
        )

        assert_rejects_empty(
            EmailVerificationToken,
            ValidationError,
            "Verification token cannot be empty",
        )
