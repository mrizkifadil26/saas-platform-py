import uuid
from dataclasses import dataclass

from iam.identity.domain import (
    EmailVerification,
    User,
)
from iam.identity.domain.value_objects import (
    Email,
    EmailVerificationToken,
    UserId,
)
from iam.shared.application import Clock
from iam.shared.application.outbox import OutboxWriter
from iam.shared.application.unit_of_work import UnitOfWork

from .commands import (
    RegisterUserCommand,
    ResendEmailVerificationCommand,
    VerifyEmailCommand,
)
from .dto import EmailVerificationResult, RegisterUserResult, UserDTO
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
    user_repository: UserRepository
    verification_repository: EmailVerificationRepository

    token_generator: EmailVerificationTokenGenerator
    token_hasher: EmailVerificationTokenHasher

    clock: Clock
    outbox: OutboxWriter
    uow: UnitOfWork

    async def execute(
        self,
        command: RegisterUserCommand,
    ) -> RegisterUserResult:
        now = self.clock.now()
        email = Email(command.email)

        existing_user = await self.user_repository.find_by_email(email)
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

        async with self.uow:
            await self.user_repository.save(user)
            await self.verification_repository.save(verification)

            await self.outbox.add(
                id=uuid.uuid4(),
                topic="iam.email_verification_requested",
                payload={
                    "user_id": str(user.id),
                    "email": user.email.value,
                    "verification_token": token_hash,
                },
            )

            await self.uow.commit()

        # send email

        return RegisterUserResult(
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
class VerifyEmailUseCase:
    user_repository: UserRepository
    verification_repository: EmailVerificationRepository

    token_hasher: EmailVerificationTokenHasher
    clock: Clock

    async def execute(
        self,
        command: VerifyEmailCommand,
    ) -> EmailVerificationResult:
        now = self.clock.now()

        raw_token = EmailVerificationToken(command.token)
        token_hash = self.token_hasher.hash(raw_token)

        verification = await self.verification_repository.find_by_token_hash(token_hash)
        if verification is None:
            raise InvalidEmailVerificationTokenError()

        if verification.is_expired(now):
            raise EmailVerificationExpiredError()

        user = await self.user_repository.find_by_id(verification.user_id)
        if user is None:
            raise UserNotFoundError()

        user.mark_email_as_verified(verified_at=now)
        verification.mark_verified(verified_at=now)

        await self.user_repository.save(user)
        await self.verification_repository.save(verification)
        # TODO: uow commit here

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


class ReactivateUseUseCase:
    async def execute(self): ...
