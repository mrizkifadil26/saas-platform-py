from dataclasses import dataclass

from iam.authorization.application.ports import PermissionCacheInvalidator
from iam.authorization.domain.value_objects import RoleId
from iam.identity.domain.value_objects import UserId
from iam.shared.application.cache import Cache


@dataclass(slots=True)
class RedisPermissionCacheInvalidator(
    PermissionCacheInvalidator,
):
    cache: Cache

    async def invalidate_user_permissions(
        self,
        user_id: UserId,
    ) -> None:
        await self.cache.delete(
            f"iam:permissions:{user_id.value}",
        )

    async def invalidate_role_permissions(
        self,
        role_id: RoleId,
    ) -> None:
        # TOOD: don't flush all authorization caches

        await self.cache.delete_pattern(
            "iam:permissions:*",
        )
