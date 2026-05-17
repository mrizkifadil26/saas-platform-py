from iam.authentication.domain import (
    AuthenticationAttempt,
    AuthenticationAttemptRepository,
    Credential,
    CredentialRepository,
    CredentialType,
    PasswordHasher,
    TokenProvider,
)
from iam.authentication.domain.value_objects import PasswordHash
from iam.identity.domain import UserRepository
from iam.identity.domain.value_objects import EmailAddress, UserId
from iam.shared.domain.clock import Clock

from .commands import (
    AuthenticateUserCommand,
    SetupPasswordCredentialCommand,
)
from .dto import (
    AuthenticatedUser,
    AuthenticationResult,
    AuthenticationTokens,
    SetupPasswordResult,
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
        policy: LoginRateLimitPolicy,
        clock: Clock,
    ):
        self._user_repository = user_repository
        self._credential_repository = credential_repository
        self._authentication_attempt_repository = authentication_attempt_repository
        self._password_hasher = password_hasher
        self._token_provider = token_provider
        self._policy = policy
        self._clock = clock

    async def execute(
        self,
        command: AuthenticateUserCommand,
    ) -> AuthenticationResult:
        now = self._clock.now()

        email = EmailAddress(command.email)
        attempt = AuthenticationAttempt.create(
            email=email,
            ip_address=command.ip_address,
            user_agent=command.user_agent,
            attempted_at=now,
        )

        credential = await self._credential_repository.find_password_by_email(email)
        if credential is None:
            # TODO: mark as failure
            # TODO: save to repo
            # TODO: raise invalid credential exception
            raise

        if await self._policy.is_locked(
            # user.id,
            credential.user_id,
            now=now,
        ):
            # TODO: mark as failure
            # TODO: save to repo
            # TODO: raise blocked exception
            raise

        credential.ensure_active()

        is_valid = await self._password_hasher.verify(
            command.password,
            credential.secret_hash.value,
        )

        if not is_valid:
            # TODO: mark as failure
            # failure_reason = "Invalid password"
            # attempt.mark_as_failure(
            #     failure_reason=failure_reason,
            #     attempted_at=now,
            # )
            # TODO: save to repo
            # await self._authentication_attempt_repository.save(attempt)
            # TODO: raise invalid credential exception
            # raise InvalidCredentials("Invalid email or password")
            raise

        user = await self._user_repository.find_by_id(credential.user_id)
        if user is None:
            # TODO: mark as failure
            # TODO: save to repo
            # TODO: raise invalid credentials exceptions
            raise

        # TODO: needs rehash password if the hash is outdated

        # TODO: create authentication session

        access_token = await self._token_provider.generate_access_token(user.id)
        refresh_token = await self._token_provider.generate_refresh_token(user.id)

        tokens = AuthenticationTokens(
            access_token=access_token,
            refresh_token=refresh_token,
        )

        attempt.mark_as_successful(user_id=user.id)
        await self._authentication_attempt_repository.save(attempt)

        # TODO: touch last_login_at
        # TODO: save to user repo

        return AuthenticationResult(
            authenticated_user=AuthenticatedUser(
                user_id=user.id,
                # session_id=session.id,
            ),
            tokens=tokens,
        )


class SetupPasswordCredentialUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        credential_repository: CredentialRepository,
        password_hasher: PasswordHasher,
        clock: Clock,
    ) -> None:
        self._user_repository = user_repository
        self._credential_repository = credential_repository
        self._password_hasher = password_hasher
        self._clock = clock

    async def execute(
        self,
        command: SetupPasswordCredentialCommand,
    ) -> SetupPasswordResult:
        now = self._clock.now()

        # payload = await self._token_provider.verify_token(command.token)
        user_id = UserId(command.user_id)
        user = await self._user_repository.find_by_id(user_id)
        if user is None:
            # TODO: raise user not found exception
            raise

        existing = await self._credential_repository.find_by_user_and_type(
            user.id,
            CredentialType.PASSWORD,
        )
        if existing is not None:
            # TODO: raise credential exists
            raise

        plain_password = command.password
        password_hash = await self._password_hasher.hash(plain_password)

        credential = Credential.password(
            user_id=user.id,
            secret_hash=PasswordHash(password_hash),
            created_at=now,
        )

        await self._credential_repository.save(credential)

        return SetupPasswordResult(
            user_id=user.id.value,
        )
