from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from iam.authentication.application import CredentialVerifier
from iam.authentication.application.ports import LoginThrottle
from iam.authentication.application.use_cases import SessionIssuer
from iam.authentication.infrastructure.security import Argon2CredentialVerifier
from iam.identity.application.ports import UserRepository
from iam.identity.infrastructure.database import SQLAlchemyUserRepository
from iam.sessions.domain import SessionRepository
from iam.sessions.infrastructure.database.repositories import (
    SQLAlchemySessionRepository,
)
from iam.shared.application import Clock


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
