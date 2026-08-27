from typing import Protocol

from iam.identity.domain.value_objects import UserId

from .role import Role
from .value_objects import RoleId


class RoleAssignmentRepository(Protocol):
    async def assign_role(
        self,
        user_id: UserId,
        role_id: RoleId,
    ) -> None: ...

    async def revoke_role(
        self,
        user_id: UserId,
        role_id: RoleId,
    ) -> None: ...

    async def is_assigned(
        self,
        user_id: UserId,
        role_id: RoleId,
    ) -> bool: ...

    async def list_role_ids_for_user(
        self,
        user_id: UserId,
    ) -> list[RoleId]: ...


class RoleRepository(Protocol):
    async def add(
        self,
        role: Role,
    ) -> None: ...

    async def save(
        self,
        role: Role,
    ) -> None: ...

    async def find_by_id(
        self,
        role_id: RoleId,
    ) -> Role | None: ...

    async def find_by_name(
        self,
        name: str,
    ) -> Role | None: ...

    async def delete(
        self,
        role_id: RoleId,
    ) -> None: ...
