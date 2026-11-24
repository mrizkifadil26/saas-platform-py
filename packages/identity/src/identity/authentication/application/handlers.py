from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from identity.credentials.application.ports import CredentialRepository, CredentialVerifier
from identity.sessions.application.ports import SessionRepository
from identity.sessions.domain.value_objects import SessionId
from identity.shared.application.command_bus.contracts import CommandHandler
from identity.shared.application.request_context import RequestContext
from identity.shared.domain.email import EmailAddress
from identity.shared.infrastructure.time.clock import Clock

from .commands import AuthenticateWithPassword, Logout
from .dto import AuthenticationResult, LogoutResult


@dataclass(slots=True)
class AuthenticateWithPasswordHandler(
    CommandHandler[
        AuthenticateWithPassword,
        AuthenticationResult,
    ]
):
    credentials: CredentialRepository
    verifier: CredentialVerifier

    # login_throttle: LoginThrottle
    # session_issuer: SessionIssuer
    # authentication_recorder: AuthenticationRecorder
    
    # TODO: add risk
    # risk_control: RiskControl

    db_session: AsyncSession
    clock: Clock

    async def __call__(
        self,
        command: AuthenticateWithPassword,
        *,
        context: RequestContext,
    ) -> AuthenticationResult:
        now = self.clock.now()
        email = EmailAddress(command.email)

        async with self.db_session.begin():
            credential = await self.credentials.find_password_by_email(
                email=email,
            )

            if credential is None:
                # TODO: Throttle record failure
                raise InvalidCredentials()

            valid = await self.verifier.verify(
                command.password,
                credential.password_hash,
            )

            if not valid:
                # TODO: Throttle record failure
                raise InvalidCredentials()

            session, token_pair = await self.session_manager.issue(
                user_id=credential.user_id,
                now=now,
                context=context,
            )

            # TODO: Auth record success (DB)

        # TODO: Throttle record success (Redis)

        return AuthenticationResult(
            user_id=credential.user_id,
            session_id=session.id,
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
            expires_at=token_pair.access_token.expires_at,
        )

    # async def execute(
    #     self,
    #     command: AuthenticateUserCommand,
    # ) -> AuthenticationResult:
    #     now = self.clock.now()
    #     email = Email(command.email)

    #     throttle = await self.login_throttle.acquire(
    #         email=email,
    #         ip_address=command.ip_address,
    #     )
    #     if not throttle.allowed:
    #         # raise AuthenticationThrottledError
    #         raise

    #     credential = await self.credential_repository.find_password_by_email(email)
    #     if credential is None:
    #         # self._record_failure()
    #         # self.login_throttle.record_failure()

    #         # raise InvalidCredentialsError
    #         raise

    #     is_valid = self.credential_verifier.verify_password(
    #         password=command.password,
    #         password_hash=credential.secret_hash,
    #     )

    #     if not is_valid:
    #         # self._record_failure()
    #         # self.login_throttle.record_failure()

    #         # raise InvalidCredentialsError
    #         raise

    #     # self.login_throttle.record_success()
    #     # attempt = AuthenticationAttempt.succeeded(
    #     #     email=email,
    #     #     user_id=credential.user_id,
    #     #     ip_address=command.ip_address,
    #     #     user_agent=command.user_agent,
    #     #     attempted_at=now,
    #     # )
    #     # await self._authentication_attempt_repository.save(attempt)

    #     # TODO: use principal if authz completed
    #     # principal = AuthenticatedPrincipal(
    #     #     user_id=credential.user_id,
    #     #     email=email,
    #     #     roles=credential.roles,
    #     # )

    #     issued = await self.session_issuer.issue(
    #         user_id=credential.user_id,
    #         # email=email,
    #         issued_at=now,
    #     )

    #     # TODO: touch last_login_at
    #     # TODO: save to user repo

    #     return AuthenticationResult(
    #         user_id=credential.user_id.value,
    #         session_id=issued.session_id.value,
    #         access_token=issued.access_token.value,
    #         refresh_token=issued.refresh_token.value,
    #     )


@dataclass(slots=True)
class LogoutHandler(
    CommandHandler[
        Logout,
        LogoutResult,
    ]
):
    sessions: SessionRepository
    
    async def __call__(
        self, 
        command: Logout,
        *, 
        context: RequestContext,
    ) -> LogoutResult:
        await self.sessions.revoke_session(
            SessionId(command.session_id)
        )

        return LogoutResult(
            message="logout success"
        )
