from datetime import timedelta

from iam.sessions.domain import (
    RefreshToken,
    RefreshTokenGenerator,
    RefreshTokenHasher,
    Session,
    SessionRepository,
)
from iam.shared.domain.clock import Clock

from .commands import (
    CreateSessionCommand,
    RevokeAllSessionsCommand,
    RevokeSessionCommand,
)
from .dto import SessionResult, SessionTokens
from .interfaces import AccessTokenProvider
from .queries import ValidateSessionQuery


class CreateSessionUseCase:
    def __init__(
        self,
        session_repository: SessionRepository,
        refresh_token_generator: RefreshTokenGenerator,
        refresh_token_hasher: RefreshTokenHasher,
        access_token_provider: AccessTokenProvider,
        clock: Clock,
        session_duration: timedelta,
        refresh_token_duration: timedelta,
    ):
        self._session_repository = session_repository
        self._refresh_token_generator = refresh_token_generator
        self._refresh_token_hasher = refresh_token_hasher
        self._access_token_provider = access_token_provider
        self._clock = clock
        self._session_duration = session_duration
        self._refresh_token_duration = refresh_token_duration

    async def execute(
        self,
        command: CreateSessionCommand,
    ) -> SessionResult:
        now = self._clock.now()

        raw_refresh_token = self._refresh_token_generator.generate()
        hashed_refresh_token = self._refresh_token_hasher.hash(
            raw_refresh_token,
        )
        refresh_token = RefreshToken.create(
            token_hash=hashed_refresh_token,
            created_at=now,
            expires_at=now + self._refresh_token_duration,
        )

        session = Session.create(
            user_id=command.user_id,
            refresh_token=refresh_token,
            created_at=now,
            expires_in=self._session_duration,
        )

        await self._session_repository.save(session)

        access_token, _ = self._access_token_provider.issue(
            session=session,
            issued_at=now,
            expires_at=now + timedelta(minutes=15),
        )

        return SessionResult(
            session_id=session.id,
            expires_at=session.expires_at,
            tokens=SessionTokens(
                access_token=access_token.value,
                refresh_token=raw_refresh_token,
            ),
        )


class ValidateSessionUseCase:
    def __init__(
        self,
        # token_hasher: TokenHasher,
        session_repository: SessionRepository,
        clock: Clock,
    ):
        # self._token_hasher = token_hasher
        self._session_repository = session_repository
        self._clock = clock

    async def execute(
        self,
        command: ValidateSessionQuery,
    ) -> None:
        now = self._clock.now()

        session = await self._session_repository.find_by_id(command.session_id)
        if session is None:
            # TODO: raise invalid session error
            # raise InvalidSession()
            raise

        if session.is_revoked:
            # TODO: raise session revoked error
            # raise SessionRevoked()
            raise

        if session.is_expired(
            now=now,
        ):
            # TODO: raise session expired error
            # raise SessionExpired()
            raise


class RevokeSessionUseCase:
    def __init__(
        self,
        session_repository: SessionRepository,
        clock: Clock,
    ):
        self._session_repository = session_repository
        self._clock = clock

    async def execute(
        self,
        command: RevokeSessionCommand,
    ) -> None:
        now = self._clock.now()

        session = await self._session_repository.find_by_id(command.session_id)
        if session is None:
            # TODO: raise invalid session
            raise

        session.revoke(
            revoked_at=now,
        )

        await self._session_repository.save(session)


class RevokeAllSessionsUseCase:
    def __init__(
        self,
        session_repository: SessionRepository,
        clock: Clock,
    ) -> None:
        self._session_repository = session_repository
        self._clock = clock

    async def execute(
        self,
        command: RevokeAllSessionsCommand,
    ) -> None:
        now = self._clock.now()

        sessions = await self._session_repository.find_active_by_user_id(
            command.user_id,
        )

        for session in sessions:
            session.revoke(now)
            await self._session_repository.save(session)
