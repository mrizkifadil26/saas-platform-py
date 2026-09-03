from dataclasses import dataclass
from datetime import datetime
from types import TracebackType
from typing import Protocol, Self

from iam.identity.domain.value_objects import UserId
from iam.sessions.domain import SessionRepository
from iam.sessions.domain.repositories import RefreshTokenRepository
from iam.sessions.domain.value_objects import (
    AccessToken,
    RefreshTokenHash,
    RefreshTokenSecret,
    SessionId,
)


class RefreshTokenGenerator(Protocol):
    def generate(
        self,
    ) -> RefreshTokenSecret: ...


class RefreshTokenHasher(Protocol):
    def hash(
        self,
        raw_token: RefreshTokenSecret,
    ) -> RefreshTokenHash: ...


@dataclass(frozen=True, slots=True)
class AccessTokenClaims:
    user_id: UserId
    session_id: SessionId
    issued_at: datetime
    expires_at: datetime


class AccessTokenIssuer(Protocol):
    def issue(
        self,
        claims: AccessTokenClaims,
    ) -> AccessToken: ...


class SessionUnitOfWork(Protocol):
    sessions: SessionRepository
    refresh_tokens: RefreshTokenRepository

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
