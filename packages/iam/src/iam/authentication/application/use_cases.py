from dataclasses import dataclass
from uuid import uuid4

from iam.authentication.domain import (
    Credential,
    CredentialRepository,
    CredentialType,
)
from iam.identity.domain import UserRepository
from iam.identity.domain.value_objects import Email, UserId
from iam.sessions.application.api import SessionIssuer
from iam.shared.application import Clock

from .commands import (
    AuthenticateUserCommand,
    ChangePasswordCommand,
    ForgotPasswordCommand,
    ResetPasswordCommand,
    SetupPasswordCredentialCommand,
)
from .dto import (
    AuthenticationResult,
    SetupPasswordResult,
)
from .ports import CredentialVerifier, PasswordHasher


@dataclass(slots=True)
class AuthenticateWithPasswordUseCase:
    credential_repository: CredentialRepository
    credential_verifier: CredentialVerifier

    login_throttle: LoginThrottle
    session_issuer: SessionIssuer
    # authentication_recorder: AuthenticationRecorder

    clock: Clock

    async def execute(
        self,
        command: AuthenticateUserCommand,
    ) -> AuthenticationResult:
        now = self.clock.now()
        email = Email(command.email)

        throttle = await self.login_throttle.check()
        if not throttle.allowed:
            # raise AuthenticationThrottledError
            raise

        credential = await self.credential_repository.find_password_by_email(email)
        if credential is None:
            self._record_failure()
            self.login_throttle.record_failure()

            # raise InvalidCredentialsError
            raise

        is_valid = self.credential_verifier.verify_password(
            password=command.password,
            password_hash=credential.secret_hash,
        )

        if not is_valid:
            self._record_failure()
            self.login_throttle.record_failure()

            # raise InvalidCredentialsError
            raise

        self.login_throttle.record_success()
        # attempt = AuthenticationAttempt.succeeded(
        #     email=email,
        #     user_id=credential.user_id,
        #     ip_address=command.ip_address,
        #     user_agent=command.user_agent,
        #     attempted_at=now,
        # )
        # await self._authentication_attempt_repository.save(attempt)

        # TODO: use principal if authz completed
        # principal = AuthenticatedPrincipal(
        #     user_id=credential.user_id,
        #     email=email,
        #     roles=credential.roles,
        # )

        issued = await self.session_issuer.issue(
            user_id=credential.user_id,
            # email=email,
            issued_at=now,
        )

        # TODO: touch last_login_at
        # TODO: save to user repo

        return AuthenticationResult(
            user_id=credential.user_id.value,
            session_id=issued.session_id.value,
            access_token=issued.access_token.value,
            refresh_token=issued.refresh_token.value,
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


class ChangePasswordCredentialUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        credential_repository: CredentialRepository,
        password_hasher: PasswordHasher,
        credential_verifier: CredentialVerifier,
        clock: Clock,
    ) -> None:
        self._user_repository = user_repository
        self._credential_repository = credential_repository
        self._password_hasher = password_hasher
        self._credential_verifier = credential_verifier
        self._clock = clock

    async def execute(
        self,
        command: ChangePasswordCommand,
    ) -> None:
        now = self._clock.now()

        user_id = UserId(command.user_id)
        credential = await self._credential_repository.find_by_user_and_type(
            user_id,
            CredentialType.PASSWORD,
        )

        if credential is None:
            # TODO: raise credential not found error
            raise

        is_valid = self._credential_verifier.verify_password(
            password=command.current_password,
            password_hash=credential.secret_hash,
        )
        if not is_valid:
            # TODO: raise invalid credentials error
            raise

        credential.change_password(
            self._password_hasher.hash(
                command.new_password,
            ),
            at=now,
        )

        await self._credential_repository.save(credential)

        # TODO: session revoke all
        # TODO: refresh tokens revoke all


class ForgotPasswordCredentialUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        credential_repository: CredentialRepository,
        # password_hasher: PasswordHasher,
        clock: Clock,
    ) -> None:
        self._user_repository = user_repository
        self._credential_repository = credential_repository
        # self._password_hasher = password_hasher
        self._clock = clock

    async def execute(
        self,
        command: ForgotPasswordCommand,
    ) -> None:
        email = Email(command.email)
        user = await self._user_repository.find_by_email(
            email,
        )

        # TODO: is this better or just raise
        if user is None:
            return

        credential = await self._credential_repository.find_by_user_and_type(
            user.id,
            CredentialType.PASSWORD,
        )
        # TODO: this is also
        if credential is None:
            return

        # TODO: generate token
        # TODO: create password reset request (is it db stored value?)

        # TODO: notify the password reset through email


class ResetPasswordCredentialUseCase:
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
        command: ResetPasswordCommand,
    ) -> None:
        now = self._clock.now()

        # TODO: hash token

        # TODO: find the password reset tokens in db

        credential = await self._credential_repository.find_by_user_and_type(
            # TODO: get user id by reset, this is for the temp val
            UserId(uuid4()),
            CredentialType.PASSWORD,
        )
        if credential is None:
            # TODO: raise invalid password reset token
            raise

        credential.change_password(
            self._password_hasher.hash(command.new_password),
            at=now,
        )

        # TODO: password reset consumed_at

        await self._credential_repository.save(credential)
        # TODO: save password resets repo

        # TODO: revoke all sessions for user
        # TODO: revoke refresh tokens for user
