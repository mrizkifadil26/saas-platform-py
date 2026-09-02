
from iam.authentication.domain.value_objects import PasswordHash
from tests.contracts.domain.string_value_object import (
    assert_rejects_empty,
    assert_trims_whitespace,
    assert_valid_string_value_object,
)


class TestPasswordHash:
    def test_string_value_object_contract(self) -> None:
        assert_valid_string_value_object(
            PasswordHash,
            "password-hash",
        )

        assert_trims_whitespace(
            PasswordHash,
            "password-hash",
        )

        assert_rejects_empty(
            PasswordHash,
            ValueError,
            "Password hash cannot be empty",
        )
