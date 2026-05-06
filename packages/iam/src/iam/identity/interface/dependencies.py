from collections.abc import AsyncGenerator

from db.app_db import AppSessionFactory, create_app_session
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from iam.identity.application.handlers import RegisterUserHandler
from iam.identity.infrastructure.crypto.argon2_password_hasher import (
    Argon2PasswordHasher,
)
from iam.identity.infrastructure.persistence.sqlalchemy.repositories import (
    SQLAlchemyUserRepository,
)


def get_app_session_factory(request: Request) -> AppSessionFactory:
    return request.app.state.session_factory


async def get_app_session(
    session_factory: AppSessionFactory = Depends(get_app_session_factory),
) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


def get_register_user_handler(
    session: AsyncSession = Depends(get_app_session),
) -> RegisterUserHandler:
    repo = SQLAlchemyUserRepository(session)
    hasher = Argon2PasswordHasher()

    return RegisterUserHandler(
        user_repository=repo,
        password_hasher=hasher,
    )
