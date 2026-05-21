from typing import Protocol

from iam.identity.domain.value_objects import UserId

from .refresh_token import RefreshToken
from .session import Session
from .value_objects import RefreshTokenHash, SessionId


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
