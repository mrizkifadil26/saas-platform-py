import json
from dataclasses import dataclass
from datetime import timedelta

from iam.authorization.domain.permission_set import PermissionSet
from iam.authorization.domain.value_objects import Permission
from iam.identity.domain.value_objects.user_id import UserId
from iam.shared.infrastructure.persistence.cache.cache import CacheKey, CacheStore

from .ports import PermissionResolver


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
    resolver: PermissionResolver
    cache: CacheStore
    key_builder: CacheKey
    ttl: timedelta = timedelta(minutes=5)
    # cache: PermissionCache

    async def resolve(
        self,
        *,
        user_id: UserId,
    ) -> PermissionSet:
        key = self.key_builder.build(
            "authz:permissions:v1",
            str(user_id),
        )

        cached = await self.cache.get(key)
        if cached is not None:
            values = json.loads(cached)

            return PermissionSet(
                frozenset(
                    Permission(value)  # force split
                    for value in values
                )
            )

        permissions = await self.resolver.resolve(user_id)

        await self.cache.set(
            key,
            json.dumps(
                [str(permission) for permission in permissions]  # force split
            ).encode(),
            ttl=self.ttl,
        )

        return permissions
