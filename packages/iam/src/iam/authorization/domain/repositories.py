from typing import Protocol

from iam.identity.domain.value_objects import UserId

from .role import Role
from .value_objects import RoleId


class UserRoleRepository(Protocol):
    async def assign_role(
        self,
        user_id: UserId,
        role: Role,
    ) -> None: ...

    async def revoke_role(
        self,
        user_id: UserId,
        role: Role,
    ) -> None: ...

    async def list_role_ids_for_user(
        self,
        user_id: UserId,
    ) -> list[RoleId]: ...


class RoleRepository(Protocol):
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
