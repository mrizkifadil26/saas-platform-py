from dataclasses import dataclass

from iam.sessions.domain.value_objects import SessionId


@dataclass(frozen=True, slots=True)
class RefreshTokenPayload:
    session_id: SessionId
