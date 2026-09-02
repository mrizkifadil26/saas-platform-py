from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from iam.shared.domain.aggregate_root import AggregateRoot

from .value_objects import Permission, RoleId


@dataclass(slots=True)
class Role(AggregateRoot[RoleId]):
    _name: str
    _permissions: set[Permission] = field(default_factory=lambda: set[Permission]())

    def __post_init__(self) -> None:
        name = self._name.strip()
        if not name:
            raise ValueError("Role name cannot be empty")

        self._name = name

    @classmethod
    def create(
        cls,
        *,
        name: str,
        permissions: Iterable[Permission] = (),
    ) -> Role:
        role = cls(
            id=RoleId.generate(),
            _name=name,
            _permissions=set(permissions),
        )

        # TODO: emit role created event
        # event = ...
        # role.record_event(event)

        return role

    @property
    def name(self) -> str:
        return self._name

    @property
    def permissions(self) -> frozenset[Permission]:
        return frozenset(self._permissions)

    def rename(self, name: str) -> None:
        name = name.strip()
        if not name:
            raise ValueError("Role name cannot be empty")

        self._name = name

    def grant_permission(
        self,
        permission: Permission,
    ) -> None:
        self._permissions.add(permission)

        # record event
        # event = ...
        # self.record_event(event)

    def revoke_permission(
        self,
        permission: Permission,
    ) -> None:
        self._permissions.discard(permission)

        # record event
        # event = ...
        # self.record_event(event)

    def has_permission(
        self,
        permission: Permission,
    ) -> bool:
        return permission in self._permissions
