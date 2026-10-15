from dataclasses import dataclass

from iam.authorization.application.ports import PermissionResolver
from iam.authorization.domain.permission_set import PermissionSet
from iam.identity.domain.value_objects import UserId
from iam.shared.infrastructure.persistence.cache.store import CacheRegionStore


@dataclass(slots=True)
class CachedPermissionResolver:
    resolver: PermissionResolver
    cache: CacheRegionStore[PermissionSet]

    async def resolve_permissions_for_user(
        self,
        user_id: UserId,
    ) -> PermissionSet:
        cached = await self.cache.get(
            "user",
            user_id,
        )

        if cached is not None:
            return cached

        resolved = await self.resolver.resolve_permissions_for_user(
            user_id,
        )
        permissions = PermissionSet.from_iterable(resolved)

        await self.cache.set(
            permissions,
            "user",
            user_id,
        )

        return permissions
