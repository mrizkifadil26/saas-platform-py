from dataclasses import dataclass

from iam.authorization.application.ports import PermissionCache, PermissionResolver
from iam.authorization.domain.value_objects import Permission
from iam.identity.domain.value_objects import UserId


@dataclass(slots=True)
class RedisPermissionResolver(
    PermissionResolver,
):
    def __init__(
        self,
        cache: PermissionCache,
    ) -> None:
        self._cache = cache

    async def resolve_permissions_for_user(
        self,
        user_id: UserId,
    ) -> set[Permission] | None:
        return await self._cache.get(user_id)
