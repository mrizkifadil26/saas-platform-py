from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from iam.shared.domain import EntityId, ValueObject


@dataclass(frozen=True, slots=True)
class RoleId(EntityId):
    pass


@dataclass(frozen=True, slots=True)
class Permission(ValueObject[str]):
    def __post_init__(self) -> None:
        value = self.value.strip()

        if not value:
            raise ValueError("Permission cannot be empty")

        resource, separator, action = value.partition(":")

        if not separator or not resource or not action:
            raise ValueError(
                "Permission must use '<resource>:<action>' format",
            )

        object.__setattr__(self, "value", value)

    @property
    def resource(self) -> str:
        return self.value.partition(":")[0]

    @property
    def action(self) -> str:
        return self.value.partition(":")[2]

    def allows(
        self,
        required: Permission,
    ) -> bool:
        if self == required:
            return True

        return self.resource == required.resource and self.action == "*"

    def __str__(self) -> str:
        return self.value


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

    def add(self, permission: Permission) -> PermissionSet:
        return PermissionSet(
            self.permissions | {permission},
        )

    def discard(self, permission: Permission) -> PermissionSet:
        return PermissionSet(
            self.permissions - {permission},
        )

    def __contains__(self, permission: Permission) -> bool:
        return permission in self.permissions

    def __iter__(self):
        return iter(self.permissions)

    def __len__(self) -> int:
        return len(self.permissions)
