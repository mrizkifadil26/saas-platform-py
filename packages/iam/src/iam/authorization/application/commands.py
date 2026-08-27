from collections.abc import Iterable
from dataclasses import dataclass

from iam.authorization.domain.value_objects import Permission, RoleId
from iam.identity.domain.value_objects import UserId


# Role section
@dataclass(frozen=True, slots=True)
class CreateRoleCommand:
    name: str
    permissions: Iterable[Permission] = ()


@dataclass(frozen=True, slots=True)
class RenameRoleCommand:
    role_id: RoleId
    name: str


@dataclass(frozen=True, slots=True)
class GrantPermissionToRoleCommand:
    role_id: RoleId
    permission: Permission


@dataclass(frozen=True, slots=True)
class RevokePermissionFromRoleCommand:
    role_id: RoleId
    permission: Permission


# Role Assignment section
@dataclass(frozen=True, slots=True)
class AssignRoleToUserCommand:
    user_id: UserId
    role_id: RoleId


@dataclass(frozen=True, slots=True)
class UnassignRoleFromUserCommand:
    user_id: UserId
    role_id: RoleId
