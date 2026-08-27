from typing import Protocol

from iam.authorization.domain.value_objects import Permission, RoleId
from iam.identity.domain.value_objects import UserId


class PermissionCache(Protocol):
    async def get(
        self,
        user_id: UserId,
    ) -> set[Permission] | None: ...

    async def set(
        self,
        user_id: UserId,
        permissions: set[Permission],
        *,
        ttl: int | None = None,
    ) -> None: ...

    async def delete(
        self,
        user_id: UserId,
    ) -> None: ...


class PermissionResolver(Protocol):
    async def resolve_permissions_for_user(
        self,
        user_id: UserId,
    ) -> set[Permission] | None: ...


class PermissionCacheInvalidator(Protocol):
    async def invalidate_user_permissions(
        self,
        user_id: UserId,
    ) -> None: ...

    async def invalidate_role_permissions(
        self,
        role_id: RoleId,
    ) -> None: ...
