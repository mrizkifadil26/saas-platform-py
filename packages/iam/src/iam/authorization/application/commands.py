from dataclasses import dataclass

from iam.authorization.domain.value_objects import RoleId
from iam.identity.domain.value_objects import UserId


@dataclass(frozen=True, slots=True)
class CreateRoleCommand:
    name: str


@dataclass(frozen=True, slots=True)
class GrantPermissionToRoleCommand:
    role_id: RoleId
    permission: str


@dataclass(frozen=True, slots=True)
class AssignRoleToUserCommand:
    user_id: UserId
    role_id: RoleId


@dataclass(frozen=True, slots=True)
class AuthorizeCommand:
    user_id: UserId
    permission: str
