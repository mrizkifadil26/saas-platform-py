import pytest

from iam.authorization.domain.value_objects import Permission
from tests.contracts.domain.string_value_object import (
    assert_rejects_empty,
    assert_trims_whitespace,
    assert_valid_string_value_object,
)


class TestPermission:
    # Construction / validation
    def test_creates_with_valid_value(self) -> None:
        assert_valid_string_value_object(
            Permission,
            "users.read",
        )

    def test_trims_whitespace(self) -> None:
        assert_trims_whitespace(
            Permission,
            "users.read",
        )

    def test_rejects_empty_value(self) -> None:
        assert_rejects_empty(
            Permission,
            ValueError,
            "Permission cannot be empty",
        )

    @pytest.mark.parametrize(
        "value",
        [
            "users",
            ".read",
            "users.",
        ],
    )
    def test_raises_when_format_is_invalid(
        self,
        value: str,
    ) -> None:
        with pytest.raises(
            ValueError,
            match=r"Permission must use '<resource>\.<action>' format",
        ):
            Permission(value)

    # Decomposition
    def test_resource_returns_resource_part(self) -> None:
        permission = Permission("users.read")

        assert permission.resource == "users"

    def test_action_returns_action_part(self) -> None:
        permission = Permission("users.read")

        assert permission.action == "read"

    # Authorization semantics
    def test_allows_same_permission(self) -> None:
        permission = Permission("users.read")
        required = Permission("users.read")

        assert permission.allows(required) is True

    def test_wildcard_allows_action_for_same_resource(self) -> None:
        permission = Permission("users.*")
        required = Permission("users.read")

        assert permission.allows(required) is True

    def test_wildcard_does_not_allow_other_resource(self) -> None:
        permission = Permission("users.*")
        required = Permission("roles.read")

        assert permission.allows(required) is False

    def test_specific_action_does_not_allow_other_action(self) -> None:
        permission = Permission("users.read")
        required = Permission("users.write")

        assert permission.allows(required) is False

    def test_specific_permission_does_not_allow_wildcard_requirement(self) -> None:
        permission = Permission("users.read")
        required = Permission("users.*")

        assert permission.allows(required) is False
