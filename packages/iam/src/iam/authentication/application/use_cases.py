from datetime import UTC, datetime

from iam.authentication.domain import (
    AuthenticationAttempt,
    AuthenticationAttemptRepository,
    Credential,
    CredentialRepository,
)
from iam.authentication.domain.value_objects import PasswordHash
from iam.identity.domain import User, UserRepository

from .commands import (
    AuthenticateUserCommand,
    RequestRegistrationCommand,
    SetupPasswordCommand,
    VerifyEmailCommand,
)
from .dto import (
    AuthenticatedUser,
    AuthenticationResult,
    AuthenticationTokens,
    RegistrationResult,
    SetupPasswordResult,
    VerifyEmailResult,
)
from .interfaces import (
    PasswordHasher,
    RegistrationTokenProvider,
    TokenProvider,
)
from .policies import LoginRateLimitPolicy


class AuthenticateWithPasswordUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        credential_repository: CredentialRepository,
        authentication_attempt_repository: AuthenticationAttemptRepository,
        password_hasher: PasswordHasher,
        token_provider: TokenProvider,
        authenticate_policy: LoginRateLimitPolicy,
    ):
        self._user_repository = user_repository
        self._credential_repository = credential_repository
        self._authentication_attempt_repository = authentication_attempt_repository
        self._password_hasher = password_hasher
        self._token_provider = token_provider
        self._authenticate_policy = authenticate_policy

    async def execute(
        self,
        command: AuthenticateUserCommand,
    ) -> AuthenticationResult:
        now = datetime.now(UTC)

        user = await self._user_repository.find_by_email(command.email)
        if user is None:
            # TODO: raise invalid credentials exceptions
            raise

        if await self._authenticate_policy.is_locked(user.id, now=now):
            # TODO: raise blocked exception
            raise

        credential = await self._credential_repository.find_by_user_id(user.id)
        if credential is None:
            # TODO: raise invalid credential exception
            raise

        is_valid = await self._password_hasher.verify(
            command.password,
            credential.password_hash.value,
        )

        attempt = AuthenticationAttempt.create(
            user.id,
            ip_address=command.ip_address,
            user_agent=command.user_agent,
            attempted_at=now,
        )
        if not is_valid:
            failure_reason = "Invalid password"
            attempt.mark_as_failure(
                failure_reason=failure_reason,
                attempted_at=now,
            )
            await self._authentication_attempt_repository.save(attempt)
            # TODO: raise invalid credential exception
            # raise InvalidCredentials("Invalid email or password")
            raise

        # TODO: needs rehash password if the hash is outdated

        # TODO: create authentication session

        access_token = await self._token_provider.generate_access_token(user.id)
        refresh_token = await self._token_provider.generate_refresh_token(user.id)

        tokens = AuthenticationTokens(
            access_token=access_token,
            refresh_token=refresh_token,
        )

        attempt.mark_as_successful(attempted_at=now)
        await self._authentication_attempt_repository.save(attempt)

        return AuthenticationResult(
            authenticated_user=AuthenticatedUser(
                user_id=user.id,
                # session_id=session.id,
            ),
            tokens=tokens,
        )


class RegisterUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        registration_token_provider: RegistrationTokenProvider,
    ) -> None:
        self._user_repository = user_repository
        self._registration_token_provider = registration_token_provider

    async def execute(
        self,
        command: RequestRegistrationCommand,
    ) -> RegistrationResult:
        now = datetime.now(UTC)

        existing_user = await self._user_repository.find_by_email(command.email)
        if existing_user is not None:
            raise

        user = User.register(
            command.email,
            registered_at=now,
        )

        await self._user_repository.save(user)

        verification_token = await self._registration_token_provider.generate_token(
            user.id,
            issued_at=now,
        )

        # TODO: send verification email with the token

        return RegistrationResult(
            user_id=user.id,
            verification_token=verification_token,
        )


class VerifyEmailUseCase:
    def __init__(
        self,
        token_provider: RegistrationTokenProvider,
        repository: UserRepository,
    ) -> None:
        self._token_provider = token_provider
        self._repository = repository

    async def execute(
        self,
        command: VerifyEmailCommand,
    ) -> VerifyEmailResult:
        now = datetime.now(UTC)

        payload = await self._token_provider.verify_token(command.token)
        user = await self._repository.find_by_id(payload.user_id)
        if user is None:
            # TODO: raise invalid token exception
            raise

        user.verify_email(verified_at=now)
        await self._repository.save(user)

        return VerifyEmailResult(
            user_id=user.id,
        )


class SetupPasswordUseCase:
    def __init__(
        self,
        token_provider: RegistrationTokenProvider,
        user_repository: UserRepository,
        credential_repository: CredentialRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._token_provider = token_provider
        self._user_repository = user_repository
        self._credential_repository = credential_repository
        self._password_hasher = password_hasher

    async def execute(
        self,
        # token: str,
        # password: str,
        command: SetupPasswordCommand,
    ) -> SetupPasswordResult:
        now = datetime.now(UTC)

        payload = await self._token_provider.verify_token(command.token)
        user = await self._user_repository.find_by_id(payload.user_id)
        if user is None:
            # TODO: raise user not found exception
            raise

        credential_by_user = await self._credential_repository.find_by_user_id(user.id)
        if credential_by_user is not None:
            # TODO: raise password already set exception
            raise

        password_hash = await self._password_hasher.hash(command.password)
        credential = Credential.create(
            user_id=user.id,
            password_hash=PasswordHash(password_hash),
            created_at=now,
        )

        await self._credential_repository.save(credential)

        return SetupPasswordResult(
            user_id=user.id,
        )
