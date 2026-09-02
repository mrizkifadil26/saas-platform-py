from dataclasses import dataclass

from iam.authorization.domain.permission_set import PermissionSet
from iam.identity.domain.value_objects import UserId
from iam.shared.infrastructure.persistence.cache.store import CacheRegionStore


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
