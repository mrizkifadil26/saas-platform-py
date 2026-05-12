from dataclasses import dataclass

from iam.sessions.domain import Session


@dataclass(frozen=True, slots=True)
class CreateSessionResult:
    token: str
    session: Session
