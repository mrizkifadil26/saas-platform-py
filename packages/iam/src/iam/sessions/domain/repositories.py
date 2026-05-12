from typing import Protocol

from .session import Session
from .value_objects import SessionId


class SessionRepository(Protocol):
    async def save(self, session: Session) -> None: ...

    async def get_by_id(self, session_id: SessionId) -> Session | None: ...

    async def get_by_token_hash(self, token_hash: str) -> Session | None: ...
