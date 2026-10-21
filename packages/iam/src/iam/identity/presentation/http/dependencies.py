from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request

from db import Database
from db.session import AsyncSession
from iam.accounts.infrastructure.database.repositories import (
    SQLAlchemyEmailVerificationRepository,
    SQLAlchemyUserRepository,
)
from iam.registration.application.handlers import VerifyEmailUseCase
from iam.shared.application.unit_of_work import IAMUnitOfWork
from iam.shared.infrastructure.database.uow import SQLAlchemyIAMUnitOfWork
from iam.shared.infrastructure.time.clock import Clock


def get_db(request: Request) -> Database:
    return request.app.state.db


DatabaseDep = Annotated[Database, Depends(get_db)]


async def get_db_session(
    db: DatabaseDep,
) -> AsyncIterator[AsyncSession]:
    async with db.session_factory() as session:
        yield session


DbSessionDep = Annotated[
    AsyncSession,
    Depends(get_db_session),
]


async def get_clock(request: Request) -> Clock:
    return request.app.state.clock


ClockDep = Annotated[
    Clock,
    Depends(get_clock),
]


async def get_iam_uow(
    db: DatabaseDep,
) -> AsyncIterator[IAMUnitOfWork]:
    uow = SQLAlchemyIAMUnitOfWork(db.session_factory)

    async with uow:
        yield uow


IAMUowDep = Annotated[
    IAMUnitOfWork,
    Depends(get_iam_uow),
]


def get_verify_email_use_case(
    clock: ClockDep,
    db_session: DbSessionDep,
) -> VerifyEmailUseCase:
    users = SQLAlchemyUserRepository(db_session)
    verifications = SQLAlchemyEmailVerificationRepository(db_session)

    return VerifyEmailUseCase(
        db_session=db_session,
        users=users,
        verifications=verifications,
        clock=clock,
    )


VerifyEmailUseCaseDep = Annotated[
    VerifyEmailUseCase,
    Depends(get_verify_email_use_case),
]
