from iam.authentication.domain import (
    AuthenticationAttempt,
    AuthenticationAttemptRepository,
    TokenProvider,
)
from iam.identity.domain import UserRepository
from iam.shared.domain.clock import Clock

from .commands import (
    AuthenticateUserCommand,
)
from .dto import (
    AuthenticatedUser,
    AuthenticationResult,
    AuthenticationTokens,
)
from .policies import LoginRateLimitPolicy


class AuthenticateWithPasswordUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        authentication_attempt_repository: AuthenticationAttemptRepository,
        # password_hasher: PasswordHasher,
        token_provider: TokenProvider,
        policy: LoginRateLimitPolicy,
        clock: Clock,
    ):
        self._user_repository = user_repository
        self._authentication_attempt_repository = authentication_attempt_repository
        # self._password_hasher = password_hasher
        self._token_provider = token_provider
        self._policy = policy
        self._clock = clock

    async def execute(
        self,
        command: AuthenticateUserCommand,
    ) -> AuthenticationResult:
        now = self._clock.now()

        user = await self._user_repository.find_by_email(command.email)
        if user is None:
            # TODO: raise invalid credentials exceptions
            raise

        if await self._policy.is_locked(user.id, now=now):
            # TODO: raise blocked exception
            raise

        # credential = await self._credential_repository.find_by_user_id(user.id)
        # if credential is None:
        # TODO: raise invalid credential exception
        # raise

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


class SetupPasswordCredentialUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        clock: Clock,
    ) -> None:
        self._user_repository = user_repository
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

        plain_password = command.password
        password_hash = await self._password_hasher.hash(plain_password)

        credential = Credential.password(
            secret_hash=PasswordHash(password_hash),
            created_at=now,
        )
        user.setup_password_credential(
            credential=credential,
            setup_at=now,
        )

        await self._user_repository.save(user)

        return SetupPasswordResult(
            user_id=user.id.value,
        )
