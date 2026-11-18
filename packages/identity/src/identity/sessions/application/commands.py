from dataclasses import dataclass

from identity.identity.domain.value_objects import UserId
from identity.sessions.domain.value_objects import SessionId
from identity.shared.application.command_bus.contracts import Command


@dataclass(frozen=True, slots=True)
class RefreshSession(Command):
    refresh_token: str


@dataclass(frozen=True, slots=True)
class RevokeSessionCommand:
    session_id: SessionId


@dataclass(frozen=True, slots=True)
class RevokeAllSessionsCommand:
    user_id: UserId
