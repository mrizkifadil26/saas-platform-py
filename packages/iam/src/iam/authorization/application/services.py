from dataclasses import dataclass

from iam.authorization.domain.permission_set import PermissionSet
from iam.authorization.domain.value_objects import Permission
from iam.identity.domain.value_objects.user_id import UserId

from .ports import PermissionCache, PermissionResolver


@dataclass(slots=True)
class AuthorizationService:
    permissions: PermissionResolver

    async def authorize(
        self,
        *,
        user_id: UserId,
        required: Permission,
    ) -> bool:
        permissions = await self.permissions.resolve(
            user_id=user_id,
        )

        return permissions.allows(required)


@dataclass(slots=True)
class CachedPermissionResolver:
    cache: PermissionCache
    resolver: PermissionResolver

    async def resolve(
        self,
        *,
        user_id: UserId,
    ) -> PermissionSet:
        cached = await self.cache.get(user_id=user_id)
        if cached is not None:
            return cached

        permissions = await self.resolver.resolve(
            user_id=user_id,
        )

        await self.cache.set(
            user_id=user_id,
            permissions=permissions,
        )

        return permissions
