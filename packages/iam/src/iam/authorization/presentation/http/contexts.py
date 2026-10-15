from __future__ import annotations

from dataclasses import dataclass

from db import Database
from iam.authorization.application.services import (
    AuthorizationService,
    CachedPermissionResolver,
    PermissionCache,
)
from iam.authorization.infrastructure.database.repositories import SQLAlchemyPermissionRepository
from iam.shared.infrastructure.cache.redis.cache import RedisCacheStore
from iam.shared.infrastructure.cache.redis.client import RedisClient


@dataclass(frozen=True, slots=True)
class AuthorizationContext:
    service: AuthorizationService

    @classmethod
    def create(
        cls,
        db: Database,
        redis: RedisClient,
    ) -> AuthorizationContext:
        cache_store = RedisCacheStore(redis.client)
        permission_repository = SQLAlchemyPermissionRepository(db)

        permission_cache = PermissionCache(cache_store)
        permissions = CachedPermissionResolver(
            repository=permission_repository,
            cache=permission_cache,
        )

        return AuthorizationContext(
            service=AuthorizationService(
                permissions=permissions,
            ),
        )
