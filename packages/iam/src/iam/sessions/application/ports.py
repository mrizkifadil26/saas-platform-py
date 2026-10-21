from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from iam.accounts.domain.value_objects import UserId
from iam.sessions.domain.refresh_token import RefreshToken
from iam.sessions.domain.session import Session
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


class AccessTokenVerifier(Protocol):
    def verify(
        self,
        token: AccessToken,
    ) -> AccessTokenClaims | None: ...


class SessionRepository(Protocol):
    async def save(self, session: Session) -> None: ...

    async def find_by_id(
        self,
        session_id: SessionId,
    ) -> Session | None: ...

    async def find_active_by_user_id(
        self,
        user_id: UserId,
    ) -> list[Session]: ...


class RefreshTokenRepository(Protocol):
    async def save(self, session: RefreshToken) -> None: ...

    async def update(self, session: RefreshToken) -> None: ...

    async def find_by_token_hash(
        self,
        token_hash: RefreshTokenHash,
    ) -> RefreshToken | None: ...
