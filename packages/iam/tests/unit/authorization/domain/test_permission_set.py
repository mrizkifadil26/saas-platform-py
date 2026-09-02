from iam.authorization.domain import PermissionSet
from iam.authorization.domain.value_objects import Permission


class TestPermissionSet:
    # Construction
    def test_from_iterable_creates_permission_set(self) -> None:
        read = Permission("users.read")
        write = Permission("users.write")

        permission_set = PermissionSet.from_iterable(
            [read, write],
        )

        assert permission_set.permissions == frozenset({read, write})

    def test_from_iterable_removes_duplicates(self) -> None:
        permission = Permission("users.read")
        permission_set = PermissionSet.from_iterable(
            [permission, permission],
        )

        assert len(permission_set) == 1

    def test_from_iterable_allows_empty_iterable(self) -> None:
        permission_set = PermissionSet.from_iterable([])

        assert len(permission_set) == 0

    # Authorization
    def test_allows_exact_permission(self) -> None:
        permission_set = PermissionSet.from_iterable(
            [Permission("users.read")],
        )

        assert permission_set.allows(
            Permission("users.read"),
        )

    def test_allows_permission_through_wildcard(self) -> None:
        permission_set = PermissionSet.from_iterable(
            [Permission("users.*")],
        )

        assert permission_set.allows(
            Permission("users.read"),
        )

    def test_does_not_allow_unmatched_permission(self) -> None:
        permission_set = PermissionSet.from_iterable(
            [Permission("users.read")],
        )

        assert not permission_set.allows(
            Permission("users.write"),
        )

    # Collection behavior
    def test_contains_permission(self) -> None:
        permission_set = PermissionSet.from_iterable(
            [Permission("users.read")],
        )

        assert Permission("users.read") in permission_set

    def test_does_not_contain_permission(self) -> None:
        permission_set = PermissionSet.from_iterable(
            [Permission("users.read")],
        )

        assert Permission("users.write") not in permission_set

    def test_iterates_over_permissions(self) -> None:
        permissions = {
            Permission("users.read"),
            Permission("users.write"),
        }

        permission_set = PermissionSet.from_iterable(
            permissions,
        )

        assert set(permission_set) == permissions

    def test_len_returns_number_of_permissions(self) -> None:
        permission_set = PermissionSet.from_iterable(
            [
                Permission("users.read"),
                Permission("users.write"),
            ]
        )

        assert len(permission_set) == 2
