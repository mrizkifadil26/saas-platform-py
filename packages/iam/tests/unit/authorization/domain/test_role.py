import pytest

from iam.authorization.domain import Role
from iam.authorization.domain.value_objects import Permission


class TestRoleCreate:
    def test_create_creates_role(self) -> None:
        role = Role.create(
            name="admin",
        )

        assert role.id is not None
        assert role.name == "admin"
        assert role.permissions == frozenset()

    def test_create_with_permission(self) -> None:
        permissions = {
            Permission("users.read"),
            Permission("users.write"),
        }

        role = Role.create(
            name="admin",
            permissions=permissions,
        )

        assert role.permissions == frozenset(permissions)

    # def test_create_normalizes_name_whitespace(self) -> None:
    #     role = Role.create(
    #         name="  admin  ",
    #     )

    #     assert role.name == "admin"

    def test_create_raises_when_name_is_empty(self) -> None:
        with pytest.raises(
            ValueError,
            match="Role name cannot be empty",
        ):
            Role.create(name="")

    def test_create_raises_when_name_is_whitespace_only(self) -> None:
        with pytest.raises(
            ValueError,
            match="Role name cannot be empty",
        ):
            Role.create(name="   ")


class TestRoleRename:
    def test_rename_changes_name(self) -> None:
        role = Role.create(name="admin")

        role.rename("super-admin")

        assert role.name == "super-admin"

    # def test_rename_normalizes_name_whitespace(self) -> None:
    #     role = Role.create(name="admin")

    #     role.rename("  super-admin  ")

    #     assert role.name == "super-admin"

    def test_rename_raises_when_name_is_empty(self) -> None:
        role = Role.create(name="admin")

        with pytest.raises(
            ValueError,
            match="Role name cannot be empty",
        ):
            role.rename("")

    def test_rename_raises_when_name_is_whitespace_only(self) -> None:
        role = Role.create(name="admin")

        with pytest.raises(
            ValueError,
            match="Role name cannot be empty",
        ):
            role.rename("   ")


class TestRoleGrantPermission:
    def test_grant_permission_adds_permission(self) -> None:
        role = Role.create(name="admin")
        permission = Permission("users.read")

        role.grant_permission(permission)

        assert permission in role.permissions

    def test_grant_permission_is_idempotent(self) -> None:
        permission = Permission("users.read")

        role = Role.create(
            name="admin",
            permissions=[permission],
        )

        role.grant_permission(permission)

        assert role.permissions == frozenset({permission})


class TestRoleRevokePermission:
    def test_revoke_permission_removes_permission(self) -> None:
        permission = Permission("users.read")

        role = Role.create(
            name="admin",
            permissions=[permission],
        )

        role.revoke_permission(permission)

        assert permission not in role.permissions

    def test_revoke_missing_permission_does_nothing(self) -> None:
        role = Role.create(name="admin")
        permission = Permission("users.read")

        role.revoke_permission(permission)

        assert role.permissions == frozenset()


class TestRoleHasPermission:
    def test_has_permission_returns_true_when_granted(self) -> None:
        permission = Permission("users.read")

        role = Role.create(
            name="admin",
            permissions=[permission],
        )

        assert role.has_permission(permission) is True

    def test_hash_permission_returns_false_when_not_granted(self) -> None:
        role = Role.create(name="admin")

        assert (
            role.has_permission(
                Permission("users.read"),
            )
            is False
        )
