from typing import Protocol

from identity.authorization.domain.role import Role
from identity.authorization.domain.value_objects import PermissionSet, RoleId
from identity.identity.domain.value_objects import UserId


class PermissionResolver(Protocol):
    # async def resolve_permissions_for_user(
    #     self,
    #     user_id: UserId,
    # ) -> set[Permission]: ...

    async def resolve(
        self,
        user_id: UserId,
    ) -> PermissionSet: ...


class PermissionCacheInvalidator(Protocol):
    async def invalidate_user(
        self,
        user_id: UserId,
    ) -> None: ...

    # async def invalidate_user_permissions(
    #     self,
    #     user_id: UserId,
    # ) -> None: ...

    # async def invalidate_role_permissions(
    #     self,
    #     role_id: RoleId,
    # ) -> None: ...


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


class PermissionRepository(Protocol):
    async def get_for_user(
        self,
        user_id: UserId,
    ) -> PermissionSet: ...
