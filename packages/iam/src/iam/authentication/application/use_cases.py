from datetime import timedelta

from iam.authentication.domain import (
    AuthenticationAttempt,
    AuthenticationAttemptRepository,
    AuthenticationDenialReason,
    AuthenticationPolicy,
    Credential,
    CredentialRepository,
    CredentialType,
)
from iam.identity.domain import UserRepository
from iam.identity.domain.value_objects import Email, UserId
from iam.sessions.application import (
    RefreshTokenGenerator,
    RefreshTokenHasher,
)
from iam.sessions.domain import RefreshToken, Session
from iam.shared.application import Clock

from .commands import (
    AuthenticateUserCommand,
    SetupPasswordCredentialCommand,
)
from .dto import (
    AuthenticationResult,
    SetupPasswordResult,
)
from .interfaces import AccessTokenIssuer, CredentialVerifier, PasswordHasher


class AuthenticateWithPasswordUseCase:
    def __init__(
        self,
        credential_repository: CredentialRepository,
        authentication_attempt_repository: AuthenticationAttemptRepository,
        credential_verifier: CredentialVerifier,
        policy: AuthenticationPolicy,
        refresh_token_generator: RefreshTokenGenerator,
        refresh_token_hasher: RefreshTokenHasher,
        access_token_issuer: AccessTokenIssuer,
        clock: Clock,
    ):
        self._credential_repository = credential_repository
        self._authentication_attempt_repository = authentication_attempt_repository
        self._credential_verifier = credential_verifier
        self._policy = policy
        self._refresh_token_generator = refresh_token_generator
        self._refresh_token_hasher = refresh_token_hasher
        self._access_token_issuer = access_token_issuer
        self._clock = clock

    async def execute(
        self,
        command: AuthenticateUserCommand,
    ) -> AuthenticationResult:
        now = self._clock.now()

        email = Email(command.email)
        credential = await self._credential_repository.find_password_by_email(email)
        if credential is None:
            attempt = AuthenticationAttempt.denied(
                email=email,
                denial_reason=AuthenticationDenialReason.INVALID_CREDENTIALS,
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

        is_valid = self._credential_verifier.verify_password(
            password=command.password,
            password_hash=credential.secret_hash,
        )

        if not is_valid:
            attempt = AuthenticationAttempt.denied(
                email=email,
                denial_reason=AuthenticationDenialReason.INVALID_CREDENTIALS,
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

        # TODO: use principal if authz completed
        # principal = AuthenticatedPrincipal(
        #     user_id=credential.user_id,
        #     email=email,
        #     roles=credential.roles,
        # )

        raw_refresh_token = self._refresh_token_generator.generate()
        refresh_token_hash = self._refresh_token_hasher.hash(
            raw_refresh_token,
        )

        session = Session.create(
            user_id=credential.user_id,
            created_at=now,
        )
        refresh_token = RefreshToken.create(
            session_id=session.id,
            token_hash=refresh_token_hash,
            created_at=now,
            expires_at=now + timedelta(days=15),
        )
        session.attach_refresh_token(
            refresh_token.id,
            now=now,
        )

        access_token = self._access_token_issuer.issue(
            claims={
                "sub": credential.user_id,
                "email": email.value,
                # "roles": credential.roles,
            }
        )

        # TODO: touch last_login_at
        # TODO: save to user repo

        return AuthenticationResult(
            user_id=credential.user_id.unwrap(),
            session_id=session.id.unwrap(),
            access_token=access_token.unwrap(),
            refresh_token=raw_refresh_token.unwrap(),
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

        user_id = UserId(command.user_id)
        user = await self._user_repository.find_by_id(user_id)
        if user is None:
            # TODO: raise user not found exception
            raise

        existing = await self._credential_repository.find_by_user_and_type(
            user_id,
            CredentialType.PASSWORD,
        )
        if existing is not None:
            # TODO: raise credential exists
            raise

        # TODO: add password setup policy later

        password_hash = self._password_hasher.hash(command.password)
        credential = Credential.password(
            user_id=user.id,
            secret_hash=password_hash,
            created_at=now,
        )

        await self._credential_repository.save(credential)

        return SetupPasswordResult(
            user_id=user.id.value,
        )
