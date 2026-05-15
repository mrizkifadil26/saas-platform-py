from iam.identity.domain import (
    EmailVerification,
    EmailVerificationRepository,
    EmailVerificationTokenGenerator,
    EmailVerificationTokenHasher,
    User,
    UserRepository,
)
from iam.identity.domain.value_objects import (
    EmailAddress,
    EmailVerificationToken,
    UserId,
)
from iam.shared.domain.clock import Clock

from .commands import (
    RegisterUserCommand,
    ResendEmailVerificationCommand,
    VerifyEmailCommand,
)
from .dto import EmailVerificationResult, RegisterUserResult
from .exceptions import UserAlreadyExistsError


class RegisterUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        verification_repository: EmailVerificationRepository,
        token_generator: EmailVerificationTokenGenerator,
        token_hasher: EmailVerificationTokenHasher,
        clock: Clock,
    ):
        self._user_repository = user_repository
        self._verification_repository = verification_repository
        self._token_generator = token_generator
        self._token_hasher = token_hasher
        self._clock = clock

    async def execute(
        self,
        command: RegisterUserCommand,
    ) -> RegisterUserResult:
        now = self._clock.now()
        email = EmailAddress(command.email)

        existing_user = await self._user_repository.find_by_email(email)
        if existing_user is not None:
            raise UserAlreadyExistsError(email.value)

        user = User.register(
            email=email,
            registered_at=now,
        )

        raw_token = self._token_generator.generate()
        token_hash = self._token_hasher.hash(raw_token)

        verification = EmailVerification.create(
            user_id=user.id,
            token_hash=token_hash,
            created_at=now,
            ttl_minutes=15,
        )

        await self._user_repository.save(user)
        await self._verification_repository.save(verification)

        return RegisterUserResult(
            user_id=user.id.unwrap(),
            email=str(user.email),
            verification_email_sent=True,
        )


class VerifyEmailUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        verification_repository: EmailVerificationRepository,
        token_hasher: EmailVerificationTokenHasher,
        clock: Clock,
    ):
        self._user_repository = user_repository
        self._verification_repository = verification_repository
        self._token_hasher = token_hasher
        self._clock = clock

    async def execute(
        self,
        command: VerifyEmailCommand,
    ) -> EmailVerificationResult:
        now = self._clock.now()

        raw_token = EmailVerificationToken(command.token)
        token_hash = self._token_hasher.hash(raw_token)

        verification = await self._verification_repository.find_by_token_hash(
            token_hash
        )
        if verification is None:
            # TODO: raise typed invalid email verification token
            raise

        verification.verify(
            token_hash,
            verified_at=now,
        )

        user = await self._user_repository.find_by_id(verification.user_id)
        if user is None:
            # TODO: raise typed user not found
            raise

        user.mark_email_as_verified(
            verified_at=now,
        )

        await self._verification_repository.save(verification)
        await self._user_repository.save(user)

        return EmailVerificationResult(
            user_id=user.id.unwrap(),
            email_verified=True,
        )


class ResendEmailVerificationUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        verification_repository: EmailVerificationRepository,
        token_generator: EmailVerificationTokenGenerator,
        token_hasher: EmailVerificationTokenHasher,
        clock: Clock,
    ):
        self._user_repository = user_repository
        self._verification_repository = verification_repository
        self._token_generator = token_generator
        self._token_hasher = token_hasher
        self._clock = clock

    async def execute(
        self,
        command: ResendEmailVerificationCommand,
    ):
        now = self._clock.now()
        user_id = UserId(command.user_id)

        user = await self._user_repository.find_by_id(user_id)
        if user is None:
            # TOOD: raise not found error
            raise

        if user.is_email_verified:
            # TODO: raise already verified error
            raise

        raw_token = self._token_generator.generate()
        token_hash = self._token_hasher.hash(raw_token)

        verification = EmailVerification.create(
            user_id=user.id,
            token_hash=token_hash,
            created_at=now,
        )

        await self._verification_repository.save(verification)

        return ...


class DeactivateUserUseCase:
    async def execute(self): ...


class ReactivateUseUseCase:
    async def execute(self): ...
