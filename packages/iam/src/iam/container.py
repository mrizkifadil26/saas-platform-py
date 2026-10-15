from __future__ import annotations

from dataclasses import dataclass

from db import Database
from iam.identity import Module as IdentityModule
from iam.shared.application.clock import Clock
from iam.shared.infrastructure.cache.redis import RedisClient


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