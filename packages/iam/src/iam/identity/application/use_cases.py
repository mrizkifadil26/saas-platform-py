from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from iam.identity import Repositories
from iam.identity.domain import (
    EmailVerification,
    User,
)
from iam.identity.domain.value_objects import (
    Email,
    EmailVerificationTokenHash,
    UserId,
)
from iam.shared.application import Clock
from iam.shared.application.messaging.message import MessageEnvelope, MessageMetadata
from iam.shared.application.unit_of_work import IAMUnitOfWork

from .commands import (
    RegisterUserCommand,
    ResendEmailVerificationCommand,
    VerifyEmailCommand,
)
from .dto import (
    EmailVerificationResult,
    RegisterUserResult,
    SendEmailVerificationRequest,
    UserDTO,
)
from .exceptions import (
    EmailVerificationExpiredError,
    InvalidEmailVerificationTokenError,
    UserAlreadyExistsError,
    UserEmailAlreadyVerifiedError,
    UserNotFoundError,
)
from .ports import (
    EmailVerificationRepository,
    EmailVerificationTokenGenerator,
    EmailVerificationTokenHasher,
    UserRepository,
)


@dataclass(slots=True)
class RegisterUserUseCase:
    uow: IAMUnitOfWork

    token_generator: EmailVerificationTokenGenerator
    token_hasher: EmailVerificationTokenHasher

    clock: Clock

    async def execute(
        self,
        command: RegisterUserCommand,
    ) -> RegisterUserResult:
        now = self.clock.now()
        raw_token = secrets.token_urlsafe(32)
        expires_at = now + self._ttl

        email = Email(command.email)

        async with self.uow:
            existing_user = await self.uow.users.find_by_email(email)
            if existing_user is not None:
                raise UserAlreadyExistsError(email.value)

            user = User.register(
                email=email,
                registered_at=now,
            )

            raw_token = self.token_generator.generate()
            token_hash = self.token_hasher.hash(raw_token)

            verification = EmailVerification.create(
                user_id=user.id,
                token_hash=token_hash,
                created_at=now,
                ttl_minutes=15,
            )

            message = MessageEnvelope(
                message_type="iam.email_verification_requested",
                payload=SendEmailVerificationRequest(
                    user_id=user.id.value,
                    email=user.email.value,
                    verification_token=raw_token.value,
                ),
                metadata=MessageMetadata.create(),
            )

            await self.uow.users.save(user)
            await self.uow.email_verifications.save(verification)
            await self.uow.outbox.add(message)

            await self.uow.commit()

        # send email

        return RegisterUserResult(
            id=str("dummy-registration-id"),
            user=UserDTO(
                id=user.id.value,
                email=user.email.value,
                is_verified=user.is_email_verified,
                created_at=user.created_at,
            ),
            email_verification_required=True,
            verification_expires_at=verification.expires_at,
        )


@dataclass(slots=True)
class IssueEmailVerification:
    uow_factory: IAMUnitOfWork
    # email_sender: EmailSender
    clock: Clock

    ttl: timedelta = timedelta(minutes=15)

    async def execute(
        self,
        user_id: UserId,
    ) -> None:
        now = self.clock.now()
        raw_token = secrets.token_urlsafe(32)
        hash_token = EmailVerificationTokenHash(
            _hash_token(raw_token),
        )
        expires_at = now + self.ttl

        async with self.uow_factory as uow:
            user = await uow.users.find_by_id(user_id)
            if user is None:
                raise UserNotFoundError

            if user.email_verified_at is not None:
                return

            verification = EmailVerification.create(
                user_id=user.id,
                token_hash=hash_token,
                created_at=now,
                expires_at=expires_at,
            )

            await uow.email_verifications.add(verification)
            await uow.commit()

        # await self._email_sender.send_verification_email(
        #     to=user.email,
        #     token=raw_token,
        #     expires_at=expires_at,
        # )


@dataclass(slots=True)
class VerifyEmailUseCase:
    db_session: AsyncSession
    verifications: EmailVerificationRepository
    users: UserRepository

    clock: Clock

    async def execute(
        self,
        command: VerifyEmailCommand,
    ) -> EmailVerificationResult:
        now = self.clock.now()

        token_hash = EmailVerificationTokenHash(
            _hash_token(command.token),
        )

        async with self.db_session.begin():
            verification = await self.verifications.find_active_token_hash_for_update(token_hash)
            if verification is None:
                raise InvalidEmailVerificationTokenError()

            if verification.is_expired(now):
                raise EmailVerificationExpiredError()

            if verification.is_verified:
                raise UserEmailAlreadyVerifiedError()

            user = await self.users.find_by_id(verification.user_id)
            if user is None:
                raise UserNotFoundError()

            user.mark_email_as_verified(verified_at=now)
            verification.mark_verified(verified_at=now)

            await self.verifications.update(verification)
            await self.users.update(user)

        return EmailVerificationResult(
            user=UserDTO(
                id=user.id.value,
                email=user.email.value,
                is_verified=user.is_email_verified,
                created_at=user.created_at,
            ),
            email_verified=True,
        )


@dataclass(slots=True)
class ResendEmailVerificationUseCase:
    user_repository: UserRepository
    verification_repository: EmailVerificationRepository

    token_generator: EmailVerificationTokenGenerator
    token_hasher: EmailVerificationTokenHasher

    clock: Clock

    async def execute(
        self,
        command: ResendEmailVerificationCommand,
    ) -> None:
        now = self.clock.now()
        user_id = UserId(command.user_id)

        user = await self.user_repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError()

        if user.is_email_verified:
            raise UserEmailAlreadyVerifiedError()

        raw_token = self.token_generator.generate()
        token_hash = self.token_hasher.hash(raw_token)

        verification = EmailVerification.create(
            user_id=user.id,
            token_hash=token_hash,
            created_at=now,
        )

        await self.verification_repository.save(verification)


class DeactivateUserUseCase:
    async def execute(self): ...


class ReactivateUserUseCase:
    async def execute(self): ...


def _hash_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf"),
    ).hexdigest()


@dataclass(slots=True)
class UseCases:
    # register: RegisterUserUseCase
    issue_verification: IssueEmailVerification
    verify_email: VerifyEmailUseCase
    resend_verification: ResendEmailVerificationUseCase
    deactivate_user: DeactivateUserUseCase
    reactivate_user: ReactivateUserUseCase

    @classmethod
    def create(
        cls,
        db_session: AsyncSession,
        clock: Clock,
        # service: Services,
        repositories: Repositories,
    ) -> UseCases:
        # register = RegisterUserUseCase()
        issue_verification = IssueEmailVerification(
            clock=clock,
            ttl=15,
        )

        verify_email = VerifyEmailUseCase(
            db_session=db_session,
            users=repositories.users,
            verifications=repositories.verifications,
            clock=clock,
        )

        resend_verification = ResendEmailVerificationUseCase(
            user_repository=repositories.users,
            verification_repository=repositories.verifications,
            clock=clock,
        )
        deactivate_user = DeactivateUserUseCase()
        reactivate_user = ReactivateUserUseCase()

        return UseCases(
            # register=register,
            issue_verification=issue_verification,
            verify_email=verify_email,
            resend_verification=resend_verification,
            deactivate_user=deactivate_user,
            reactivate_user=reactivate_user,
        )
