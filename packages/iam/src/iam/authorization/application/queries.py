from dataclasses import dataclass

from iam.authorization.domain.value_objects import Permission, RoleId
from iam.identity.domain.value_objects.user_id import UserId


@dataclass(frozen=True, slots=True)
class GetRoleQuery:
    role_id: RoleId


@dataclass(frozen=True, slots=True)
class FindRoleByNameQuery:
    name: str


@dataclass(frozen=True, slots=True)
class ListUserRoleIdsQuery:
    user_id: UserId


@dataclass(frozen=True, slots=True)
class CheckPermissionQuery:
    user_id: UserId
    permission: Permission
