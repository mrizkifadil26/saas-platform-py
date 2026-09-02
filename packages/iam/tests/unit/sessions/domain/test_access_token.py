from iam.sessions.domain.value_objects import AccessToken
from tests.contracts.domain.string_value_object import (
    assert_rejects_empty,
    assert_trims_whitespace,
    assert_valid_string_value_object,
)


class TestAccessToken:
    def test_string_value_object_contract(self) -> None:
        assert_valid_string_value_object(
            AccessToken,
            "access-token",
        )

        assert_trims_whitespace(
            AccessToken,
            "access-token",
        )

        assert_rejects_empty(
            AccessToken,
            ValueError,
            "Access token cannot be empty",
        )
