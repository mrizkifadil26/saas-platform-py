from dataclasses import dataclass

from iam.identity.domain.value_objects import UserId
from iam.sessions.domain.value_objects import SessionId


@dataclass(frozen=True, slots=True)
class CreateSessionCommand:
    user_id: UserId


@dataclass(frozen=True, slots=True)
class RevokeSessionCommand:
    session_id: SessionId
