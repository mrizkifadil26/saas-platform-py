from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from identity.accounts.infrastructure.database import SQLAlchemyUserRepository
from identity.authentication.application import CredentialVerifier
from identity.authentication.application.ports import LoginThrottle
from identity.authentication.application.use_cases import SessionIssuer
from identity.authentication.infrastructure.security import Argon2CredentialVerifier
from identity.composition import IAMContainer
from identity.identity.application.ports import UserRepository
from identity.sessions.domain import SessionRepository
from identity.sessions.infrastructure.database.repositories import (
    SQLAlchemySessionRepository,
)
from identity.shared.application import Clock


@dataclass(frozen=True, slots=True)
class Verifiers:
    credential: CredentialVerifier


@dataclass(frozen=True, slots=True)
class Throttles:
    login: LoginThrottle


@dataclass(frozen=True, slots=True)
class Issuers:
    session: SessionIssuer


@dataclass(frozen=True, slots=True)
class Dependencies:
    users: UserRepository
    sessions: SessionRepository

    verifier: Verifiers
    throttle: Throttles
    issuer: Issuers

    clock: Clock


def create_dependencies(
    *,
    db: AsyncSession,
    clock: Clock,
) -> Dependencies:
    return Dependencies(
        users=SQLAlchemyUserRepository(db),
        sessions=SQLAlchemySessionRepository(db),
        verifier=Verifiers(
            credential=Argon2CredentialVerifier(),
        ),
        throttle=Throttles(
            login=LoginThrottle(...),
        ),
        issuer=Issuers(
            session=SessionIssuer(...),
        ),
        clock=clock,
    )


def get_dependencies(
    db: Annotated[AsyncSession, Depends(get_db)],
    clock: Annotated[Clock, Depends(get_clock)],
) -> Dependencies:
    return create_dependencies(
        db=db,
        clock=clock,
    )


def get_container(request: Request):
    return request.app.state.container


def get_iam(container = Depends(get_container)) -> IAMContainer:
    return container.iam
