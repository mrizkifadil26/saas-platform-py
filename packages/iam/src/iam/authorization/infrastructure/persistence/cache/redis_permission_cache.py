import json
from dataclasses import dataclass

from iam.authorization.application.ports import PermissionCache
from iam.authorization.domain.value_objects import Permission
from iam.identity.domain.value_objects import UserId
from iam.shared.application.cache import Cache


@dataclass(slots=True)
class RedisPermissionCache(PermissionCache):
    PREFIX = "iam:authz:permissions"
    DEFAULT_TTL = 300

    def __init__(
        self,
        cache: Cache,
        *,
        ttl: int = DEFAULT_TTL,
    ) -> None:
        self._cache = cache
        self._ttl = ttl

    def _key(self, user_id: UserId) -> str:
        return f"{self.PREFIX}:user:{user_id.value}"

    async def get(
        self,
        user_id: UserId,
    ) -> set[Permission] | None:
        value = await self._cache.get(self._key(user_id))
        if value is None:
            return None

        raw_permission = json.loads(value)

        return {Permission(permission) for permission in raw_permission}

    async def set(
        self,
        user_id: UserId,
        permissions: set[Permission],
        *,
        ttl: int | None = None,
    ) -> None:
        value = json.dumps(
            [permission.value for permission in permissions],
        )

        await self._cache.set(
            self._key(user_id),
            value,
            ttl=ttl if ttl is not None else self._ttl,
        )

    async def delete(
        self,
        user_id: UserId,
    ) -> None:
        await self._cache.delete(
            self._key(user_id),
        )
