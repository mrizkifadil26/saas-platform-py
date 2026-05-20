from __future__ import annotations

from dataclasses import dataclass, field

from iam.shared.domain import Entity

from .value_objects import Permission, RoleId


@dataclass(slots=True)
class Role(Entity[RoleId]):
    name: str
    permissions: set[Permission] = field(default_factory=set[Permission])

    @classmethod
    def create(
        cls,
        name: str,
    ) -> Role:
        role = cls(
            id=RoleId.generate(),
            name=name,
        )

        # TODO: emit role created event

        return role

    def grant(
        self,
        permission: Permission,
    ) -> None:
        self.permissions.add(permission)

    def revoke(
        self,
        permission: Permission,
    ) -> None:
        self.permissions.discard(permission)

    def has_permission(
        self,
        permission: Permission,
    ) -> bool:
        return permission in self.permissions
