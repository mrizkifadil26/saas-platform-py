from dataclasses import dataclass
from datetime import datetime

from iam.shared.kernel.events import DomainEvent

from .value_objects import EmailChallengeId, RegistrationId


@dataclass(frozen=True, slots=True)
class EmailChallengeCreated(DomainEvent):
    challenge_id: EmailChallengeId
    registration_id: RegistrationId
    expires_at: datetime

    @property
    def event_type(self) -> str:
        return "email_challenge.created"


@dataclass(frozen=True, slots=True)
class EmailChallengeCompleted(DomainEvent):
    challenge_id: EmailChallengeId
    registration_id: RegistrationId
    completed_at: datetime

    @property
    def event_type(self) -> str:
        return "email_challenge.completed"
