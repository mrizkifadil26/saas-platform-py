from __future__ import annotations

from dataclasses import dataclass

from db import Database
from identity.external_identities import Module as IdentityModule
from identity.shared.infrastructure.cache.redis import RedisClient
from identity.shared.infrastructure.time.clock import Clock


@dataclass(slots=True)
class Container:
    db: Database

    identity: IdentityModule
    authentication: AuthenticationService
    authorization: AuthorizationService

    @classmethod
    def create(
        cls,
        *,
        db: Database,
        redis: RedisClient,
        clock: Clock,
    ) -> Container:
        identity = IdentityModule.create()

        authentication = IdentityService.create()
        authorization = IdentityService.create()

        return Container(
            db=db,
            identity=identity,
            authentication=authentication,
            authorization=authorization,
        )