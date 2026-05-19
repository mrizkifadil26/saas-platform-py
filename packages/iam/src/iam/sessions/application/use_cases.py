from iam.sessions.domain import (
    SessionRepository,
)
from iam.shared.domain.clock import Clock

from .commands import (
    RevokeAllSessionsCommand,
    RevokeSessionCommand,
)
from .queries import ValidateSessionQuery


class ValidateSessionUseCase:
    def __init__(
        self,
        session_repository: SessionRepository,
        clock: Clock,
    ):
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
