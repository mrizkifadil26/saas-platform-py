
from iam.sessions.domain.value_objects import RefreshTokenHash
from iam.shared.domain.exceptions import ValidationError
from tests.contracts.domain.string_value_object import (
    assert_rejects_empty,
    assert_trims_whitespace,
    assert_valid_string_value_object,
)


class TestRefreshTokenHash:
    def test_string_value_object_contract(self) -> None:
        assert_valid_string_value_object(
            RefreshTokenHash,
            "refresh-token-hash",
        )

        assert_trims_whitespace(
            RefreshTokenHash,
            "refresh-token-hash",
        )

        assert_rejects_empty(
            RefreshTokenHash,
            ValidationError,
            "Refresh token hash cannot be empty",
        )
