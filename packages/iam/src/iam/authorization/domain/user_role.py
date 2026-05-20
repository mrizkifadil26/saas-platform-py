from dataclasses import dataclass

from iam.identity.domain.value_objects import UserId

from .value_objects import RoleId


@dataclass(frozen=True, slots=True)
class UserRole:
    user_id: UserId
    role_id: RoleId
