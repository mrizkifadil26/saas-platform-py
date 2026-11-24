from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from identity.accounts.domain.value_objects import UserId
from identity.sessions.domain.refresh_token import RefreshToken
from identity.sessions.domain.session import Session
from identity.sessions.domain.value_objects import (
    AccessToken,
    RefreshTokenHash,
    RefreshTokenId,
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

    async def find_by_refresh_token_hash(
        self,
        token_hash: bytes,
    ) -> tuple[Session, RefreshToken] | None: ...

    async def rotate_refresh_token(
        self,
        *,
        current_refresh_token_id: RefreshTokenId,
        new_token_hash: bytes,
    ) -> None: ...

    async def revoke_session(
        self,
        session_id: SessionId,
    ) -> None: ...

    # TODO: revoke whole family token
    # async def revoke_token_family(
    #     self,
    #     family_id: UUID,
    # ) -> None: ...

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
