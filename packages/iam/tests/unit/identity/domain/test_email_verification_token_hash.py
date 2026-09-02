from iam.identity.domain.value_objects import (
    EmailVerificationTokenHash,
)
from iam.shared.domain.exceptions import ValidationError
from tests.contracts.domain.string_value_object import (
    assert_rejects_empty,
    assert_trims_whitespace,
    assert_valid_string_value_object,
)


class TestEmailVerificationTokenHash:
    def test_string_value_object_contract(self) -> None:
        assert_valid_string_value_object(
            EmailVerificationTokenHash,
            "hashed-token",
        )

        assert_trims_whitespace(
            EmailVerificationTokenHash,
            "hashed-token",
        )

        assert_rejects_empty(
            EmailVerificationTokenHash,
            ValidationError,
            "Verification token hash cannot be empty",
        )
