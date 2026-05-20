import json
from dataclasses import dataclass

from iam.authorization.domain import PermissionResolver
from iam.authorization.domain.value_objects import Permission
from iam.authorization.infrastructure.cache import Cache
from iam.identity.domain.value_objects import UserId


@dataclass(slots=True)
class CachedPermissionResolver(
    PermissionResolver,
):
    resolver: PermissionResolver
    cache: Cache
    ttl: int = 300

    async def resolve_permissions_for_user(
        self,
        user_id: UserId,
    ) -> set[Permission]:
        cache_key = f"iam:permissions:{user_id.value}"

        cached = await self.cache.get(cache_key)
        if cached is not None:
            values: list[str] = json.loads(cached)

            return {Permission(value) for value in values}

        permissions = await self.resolver.resolve_permissions_for_user(user_id)

        await self.cache.set(
            cache_key,
            json.dumps([permission.value for permission in permissions]),
            ttl=self.ttl,
        )

        return permissions
