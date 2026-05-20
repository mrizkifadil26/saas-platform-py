from dataclasses import dataclass

from .value_objects import Permission


@dataclass(frozen=True, slots=True)
class HasPermission:
    permission: Permission

    def is_satisfied_by(
        self,
        permissions: set[Permission],
    ) -> bool:
        return self.permission in permissions
