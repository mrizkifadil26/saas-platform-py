from iam.authentication.domain import (
    AuthenticationAttempt,
    AuthenticationAttemptRepository,
    Authenticator,
    Credential,
    CredentialRepository,
    CredentialType,
    PasswordHasher,
)
from iam.authentication.domain.enums import AuthenticationFailureReason
from iam.authentication.domain.value_objects import PasswordHash
from iam.identity.domain import UserRepository
from iam.identity.domain.value_objects import EmailAddress, UserId
from iam.sessions.domain import Session, SessionRepository
from iam.sessions.domain.session_issuer import SessionIssuer
from iam.shared.domain.clock import Clock

from .commands import (
    AuthenticateUserCommand,
    SetupPasswordCredentialCommand,
)
from .dto import (
    AuthenticationResult,
    SetupPasswordResult,
)
from .policies import AuthenticationPolicy


class AuthenticateWithPasswordUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        credential_repository: CredentialRepository,
        authentication_attempt_repository: AuthenticationAttemptRepository,
        # session_repository: SessionRepository,
        session_issuer: SessionIssuer,
        authenticator: Authenticator,
        password_hasher: PasswordHasher,
        policy: AuthenticationPolicy,
        clock: Clock,
    ):
        self._user_repository = user_repository
        self._credential_repository = credential_repository
        self._authentication_attempt_repository = authentication_attempt_repository
        self._authenticator = authenticator
        # self._session_repository = session_repository
        self._session_issuer = session_issuer
        self._password_hasher = password_hasher
        self._policy = policy
        self._clock = clock

    async def execute(
        self,
        command: AuthenticateUserCommand,
    ) -> AuthenticationResult:
        now = self._clock.now()

        email = EmailAddress(command.email)
        credential = await self._credential_repository.find_password_by_email(email)
        if credential is None:
            attempt = AuthenticationAttempt.failed(
                email=email,
                failure_reason=AuthenticationFailureReason.INVALID_CREDENTIALS,
                ip_address=command.ip_address,
                user_agent=command.user_agent,
                attempted_at=now,
            )

            await self._authentication_attempt_repository.save(attempt)
            # TODO: raise invalid credential exception
            raise

        recent_failures = (
            await self._authentication_attempt_repository.count_recent_failures(
                email=email,
                since=now - self._policy.failure_window(),
            )
        )

        self._policy.ensure_not_locked(
            recent_failures=recent_failures,
        )

        auth_result = self._authenticator.authenticate_with_password(
            credential=credential,
            password=command.password,
        )

        if auth_result.is_failure:
            attempt = AuthenticationAttempt.failed(
                email=email,
                failure_reason=auth_result.failure_reason,
                ip_address=command.ip_address,
                user_agent=command.user_agent,
                attempted_at=now,
            )

            await self._authentication_attempt_repository.save(attempt)

        attempt = AuthenticationAttempt.succeeded(
            email=email,
            user_id=credential.user_id,
            ip_address=command.ip_address,
            user_agent=command.user_agent,
            attempted_at=now,
        )

        await self._authentication_attempt_repository.save(attempt)

        # if not is_valid:
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
        # raise

        # TODO: needs rehash password if the hash is outdated

        access_token = self._access_token_generator.generate()
        refresh_token = self._refresh_token_generator.generate()

        session = await self._session_issuer.issue(
            user_id=credential.user_id,
        )

        # TODO: touch last_login_at
        # TODO: save to user repo

        return AuthenticationResult(
            user_id=credential.user_id,
            session_id=session.id,
            access_token=session.access_token,
            # refresh_token=session.refresh_token,
            refresh_token=session.active_refresh_token.token_hash.value,
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
