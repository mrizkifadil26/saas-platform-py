from __future__ import annotations

from fastapi import APIRouter

from db import Database
from iam.authentication.presentation.http.router import router as authn_router
from iam.authorization.presentation.http.router import router as authz_router
from iam.identity.context import create_identity
from iam.identity.presentation.http.router import router as identity_router
from iam.shared.application.clock import Clock
from iam.shared.infrastructure.cache.redis import RedisClient


class IAMContext:
    def __init__(
        self,
        *,
        db: Database,
        redis: RedisClient,
        clock: Clock,
        # settings: IAMSettings,
    ) -> None:
        # self.users = UserService(...)
        # self.sessions = SessionService(...)
        # self.authorization = AuthorizationService(...)

        self.identity = create_identity(
            db=db,
            clock=clock,
            # redis=redis,
        )

    @classmethod
    def create(
        cls,
        *,
        db: Database,
        redis: RedisClient,
        clock: Clock,
    ) -> IAMContext:
        return IAMContext(
            db=db,
            redis=redis,
            clock=clock,
        )

    @property
    def router(self) -> APIRouter:
        router = APIRouter()

        router.include_router(identity_router)
        router.include_router(authn_router)
        router.include_router(authz_router)

        return router
