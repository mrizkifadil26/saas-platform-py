from dataclasses import dataclass

from identity.identity.domain.value_objects import UserId

from .value_objects import RoleId


@dataclass(frozen=True, slots=True)
class RoleAssignment:
    user_id: UserId
    role_id: RoleId
