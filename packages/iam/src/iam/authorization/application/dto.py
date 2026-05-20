from dataclasses import dataclass

from iam.authorization.domain.value_objects import RoleId


@dataclass(frozen=True, slots=True)
class RoleDTO:
    id: RoleId
    name: str


@dataclass(frozen=True, slots=True)
class AuthorizationResult:
    allowed: bool
