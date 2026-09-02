from iam.sessions.domain.value_objects import RefreshTokenSecret
from iam.shared.domain.exceptions import ValidationError
from tests.contracts.domain.string_value_object import (
    assert_rejects_empty,
    assert_trims_whitespace,
    assert_valid_string_value_object,
)


class TestRefreshTokenSecret:
    def test_string_value_object_contract(self) -> None:
        assert_valid_string_value_object(
            RefreshTokenSecret,
            "refresh-token-secret",
        )

        assert_trims_whitespace(
            RefreshTokenSecret,
            "refresh-token-secret",
        )

        assert_rejects_empty(
            RefreshTokenSecret,
            ValidationError,
            "Refresh token secret cannot be empty",
        )
