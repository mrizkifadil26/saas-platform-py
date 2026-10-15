from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from iam.identity.application.ports import EmailVerificationRepository, UserRepository
from iam.identity.application.services import Services
from iam.identity.application.use_cases import UseCases
from iam.identity.infrastructure.database.repositories import (
    SQLAlchemyEmailVerificationRepository,
    SQLAlchemyUserRepository,
)
from iam.shared.application.clock import Clock

from .presentation.http.router import router


@dataclass(slots=True)
class Repositories:
    users: UserRepository
    verifications: EmailVerificationRepository

    @classmethod
    def create(
        cls,
        db_session: AsyncSession,
    ) -> Repositories:
        users = SQLAlchemyUserRepository(db_session)
        verifications = SQLAlchemyEmailVerificationRepository(db_session)

        return Repositories(
            users=users,
            verifications=verifications,
        )


@dataclass(slots=True)
class Module:
    services: Services
    use_cases: UseCases
    repositories: Repositories

    @classmethod
    def create(
        cls,
        db_session: AsyncSession,
        clock: Clock,
    ) -> Module:
        services = Services.create()
        repositories = Repositories.create(db_session)
        use_cases = UseCases.create(repositories, clock,)

        return Module(
            services=services,
            use_cases=use_cases,
            repositories=repositories,
        )


__all__ = ["Module", "router"]
