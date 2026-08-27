from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from iam.authorization.domain.value_objects import Permission


@dataclass(frozen=True, slots=True)
class PermissionSet:
    permissions: frozenset[Permission]

    @classmethod
    def from_iterable(
        cls,
        permissions: Iterable[Permission],
    ) -> PermissionSet:
        return cls(frozenset(permissions))

    def allows(self, required: Permission) -> bool:
        return any(permission.allows(required) for permission in self.permissions)

    def __contains__(self, permission: Permission) -> bool:
        return permission in self.permissions

    def __iter__(self):
        return iter(self.permissions)

    def __len__(self) -> int:
        return len(self.permissions)
