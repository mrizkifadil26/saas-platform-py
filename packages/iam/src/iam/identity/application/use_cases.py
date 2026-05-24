from iam.identity.domain import (
    EmailVerification,
    EmailVerificationRepository,
    User,
    UserRepository,
)
from iam.identity.domain.value_objects import (
    Email,
    EmailVerificationToken,
    UserId,
)
from iam.shared.application import Clock

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
from .interfaces import EmailVerificationTokenGenerator, EmailVerificationTokenHasher


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
        email = Email(command.email)

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
            user=UserDTO(
                id=user.id.unwrap(),
                email=user.email.unwrap(),
                is_verified=user.is_email_verified,
                created_at=user.created_at,
            ),
            email_verification_required=True,
            verification_expires_at=verification.expires_at,
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
            raise InvalidEmailVerificationTokenError()

        if verification.is_expired(now):
            raise EmailVerificationExpiredError()

        user = await self._user_repository.find_by_id(verification.user_id)
        if user is None:
            raise UserNotFoundError()

        user.mark_email_as_verified(verified_at=now)
        verification.mark_verified(verified_at=now)

        await self._user_repository.save(user)
        await self._verification_repository.save(verification)
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
    ) -> None:
        now = self._clock.now()
        user_id = UserId(command.user_id)

        user = await self._user_repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError()

        if user.is_email_verified:
            raise UserEmailAlreadyVerifiedError()

        raw_token = self._token_generator.generate()
        token_hash = self._token_hasher.hash(raw_token)

        verification = EmailVerification.create(
            user_id=user.id,
            token_hash=token_hash,
            created_at=now,
        )

        await self._verification_repository.save(verification)


class DeactivateUserUseCase:
    async def execute(self): ...


class ReactivateUseUseCase:
    async def execute(self): ...
