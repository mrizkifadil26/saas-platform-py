from typing import Protocol

from iam.identity.domain.value_objects import UserId

from .value_objects import Permission, RoleId


class PermissionResolver(Protocol):
    async def resolve_permissions_for_user(
        self,
        user_id: UserId,
    ) -> set[Permission]: ...


class PermissionCacheInvalidator(Protocol):
    async def invalidate_user_permissions(
        self,
        user_id: UserId,
    ) -> None: ...

    async def invalidate_role_permissions(
        self,
        role_id: RoleId,
    ) -> None: ...
