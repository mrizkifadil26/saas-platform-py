from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RoleDTO:
    id: UUID
    name: str
    permissions: frozenset[str]


@dataclass(frozen=True, slots=True)
class AuthorizationResult:
    allowed: bool
