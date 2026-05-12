from datetime import UTC, datetime, timedelta

from iam.sessions.application.queries import ValidateSessionQuery
from iam.sessions.domain import Session, SessionRepository

from .commands import CreateSessionCommand, RevokeSessionCommand
from .dto import CreateSessionResult
from .interfaces import TokenGenerator, TokenHasher


class CreateSessionUseCase:
    def __init__(
        self,
        token_generator: TokenGenerator,
        token_hasher: TokenHasher,
        session_repository: SessionRepository,
    ):
        self._token_generator = token_generator
        self._token_hasher = token_hasher
        self._session_repository = session_repository

    async def execute(
        self,
        command: CreateSessionCommand,
    ) -> CreateSessionResult:
        now = datetime.now(UTC)

        token = self._token_generator.generate()
        token_hash = self._token_hasher.hash(token)

        session = Session.create(
            user_id=command.user_id,
            token_hash=token_hash,
            ttl=timedelta(days=30),
            created_at=now,
        )

        await self._session_repository.save(session)

        return CreateSessionResult(
            token=token,
            session=session,
        )


class ValidateSessionUseCase:
    def __init__(
        self,
        token_hasher: TokenHasher,
        session_repository: SessionRepository,
    ):
        self._token_hasher = token_hasher
        self._session_repository = session_repository

    async def execute(
        self,
        command: ValidateSessionQuery,
    ) -> Session | None:
        now = datetime.now(UTC)

        token_hash = self._token_hasher.hash(command.token)

        session = await self._session_repository.get_by_token_hash(token_hash)

        if session is None or session.is_expired(now=now):
            return None

        return session


class RevokeSessionUseCase:
    def __init__(
        self,
        session_repository: SessionRepository,
    ):
        self._session_repository = session_repository

    async def execute(
        self,
        command: RevokeSessionCommand,
    ) -> None:
        session = await self._session_repository.get_by_id(command.session_id)
        if not session:
            return

        session.revoke()
        await self._session_repository.save(session)
