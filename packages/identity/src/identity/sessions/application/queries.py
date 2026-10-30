from dataclasses import dataclass

from identity.sessions.domain.value_objects import SessionId


@dataclass(frozen=True, slots=True)
class ValidateSessionQuery:
    session_id: SessionId
