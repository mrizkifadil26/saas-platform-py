from dataclasses import dataclass

from identity.authorization.domain.permission_set import PermissionSet
from identity.identity.domain.value_objects import UserId
from identity.shared.infrastructure.persistence.cache.store import CacheRegionStore


@dataclass(slots=True)
class PermissionCacheInvalidator:
    cache: CacheRegionStore[PermissionSet]

    async def invalidate_user_permissions(
        self,
        user_id: UserId,
    ) -> None:
        await self.cache.delete(
            "user",
            user_id,
        )
