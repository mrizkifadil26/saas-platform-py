from __future__ import annotations

from dataclasses import dataclass

from identity.accounts.infrastructure.database.repositories import (
    SQLAlchemyEmailVerificationRepository,
    SQLAlchemyUserRepository,
)
from identity.identity.infrastructure.security.secure_email_verification_token_generator import (
    SecureEmailVerificationTokenGenerator,
)
from identity.identity.infrastructure.security.sha256_email_verification_token_hasher import (
    Sha256EmailVerificationTokenHasher,
)
from identity.registration.application.handlers import (
    RegisterUserUseCase,
    ResendEmailVerificationUseCase,
    VerifyEmailUseCase,
)
from identity.shared.infrastructure.database.uow import SQLAlchemyUnitOfWork
from identity.shared.infrastructure.outbox.sqlalchemy.sqlalchemy_outbox_repository import (
    SQLAlchemyOutboxRepository,
)
from identity.shared.infrastructure.time.clock import Clock

from db import Database


@dataclass(frozen=True, slots=True)
class IdentityCommands:
    register_user: RegisterUserUseCase
    verify_email: VerifyEmailUseCase
    resend_email_verification: ResendEmailVerificationUseCase


@dataclass(frozen=True, slots=True)
class IdentityQueries: ...


@dataclass(frozen=True, slots=True)
class IdentityContext:
    commands: IdentityCommands
    queries: IdentityQueries

    @classmethod
    def create(
        cls,
        *,
        db: Database,
        clock: Clock,
        # redis: RedisClient,
    ) -> IdentityContext:
        user_repository = SQLAlchemyUserRepository(db)
        verification_repository = SQLAlchemyEmailVerificationRepository(db)
        outbox_repository = SQLAlchemyOutboxRepository(db)

        token_generator = SecureEmailVerificationTokenGenerator()
        token_hasher = Sha256EmailVerificationTokenHasher()

        uow = SQLAlchemyUnitOfWork(session_factory=db.session_factory)

        return IdentityContext(
            commands=IdentityCommands(
                register_user=RegisterUserUseCase(
                    user_repository=user_repository,
                    verification_repository=verification_repository,
                    outbox_repository=outbox_repository,
                    token_generator=token_generator,
                    token_hasher=token_hasher,
                    clock=clock,
                    uow=uow,
                ),
                verify_email=VerifyEmailUseCase(
                    user_repository=user_repository,
                    verification_repository=verification_repository,
                    token_hasher=token_hasher,
                    clock=clock,
                ),
                resend_email_verification=ResendEmailVerificationUseCase(
                    user_repository=user_repository,
                    verification_repository=verification_repository,
                    token_generator=token_generator,
                    token_hasher=token_hasher,
                    clock=clock,
                ),
            ),
            queries=IdentityQueries(),
        )
