from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import timedelta

from identity.authorization.domain.value_objects import Permission, PermissionSet, RoleId
from identity.identity.domain.value_objects import UserId
from identity.shared.infrastructure.cache.cache import CacheStore

from .ports import PermissionRepository, RoleAssignmentRepository


@dataclass(slots=True)
class AuthorizationService:
    permissions: CachedPermissionResolver

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
class RoleService:
    repository: RoleAssignmentRepository
    permission_cache: PermissionCache

    async def assign_role(
        self,
        user_id: UserId,
        role_id: RoleId,
    ) -> None:
        await self.repository.assign_role(user_id, role_id)

        await self.permission_cache.delete(user_id)


@dataclass(frozen=True, slots=True)
class PermissionCache:
    store: CacheStore
    ttl: timedelta = timedelta(minutes=5)

    def _key(self, user_id: UserId) -> str:
        return f"iam:authz:permissions:user:{user_id.value}"

    async def get(
        self,
        user_id: UserId,
    ) -> PermissionSet | None:
        value = await self.store.get(self._key(user_id))
        if value is None:
            return None

        permissions = json.loads(value)
        return PermissionSet.from_iterable(permission for permission in permissions)

    async def set(
        self,
        user_id: UserId,
        permissions: PermissionSet,
    ) -> None:
        value = json.dumps(
            [permission.value for permission in permissions],
        ).encode()

        await self.store.set(
            self._key(user_id),
            value,
            ttl=int(self.ttl.total_seconds()),
        )

    async def delete(
        self,
        user_id: UserId,
    ) -> None:
        await self.store.delete(
            self._key(user_id),
        )


@dataclass(slots=True)
class CachedPermissionResolver:
    repository: PermissionRepository
    cache: PermissionCache

    # key_builder: CacheKey
    # ttl: timedelta = timedelta(minutes=5)
    # cache: PermissionCache

    async def resolve(
        self,
        user_id: UserId,
    ) -> PermissionSet:
        cached = await self.cache.get(user_id)

        if cached is not None:
            return cached

        permissions = await self.repository.get_for_user(user_id)

        await self.cache.set(user_id, permissions)

        return permissions


# @dataclass(frozeon=True, slots=True)
# class AuthorizationContext:
#     principal: Principal | None
#     roles: frozenset[str]
#     permissions: frozenset[str]

#     @classmethod
#     def anonymous(cls) -> :
#         return cls(
#             principal=None,
#             roles=frozenset(),
#             permissions=frozenset(),
#         )

#     @property
#     def user_id(self) -> UUID | None:
#         return self.principal.user_id if self.principal else None
