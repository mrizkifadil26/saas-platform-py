from dataclasses import dataclass
from datetime import datetime

from identity.shared.kernel.events import DomainEvent

from .value_objects import EmailChallengeId, RegistrationId


@dataclass(frozen=True, slots=True)
class EmailChallengeCreated(DomainEvent):
    event_type = "email_challenge.created"

    challenge_id: EmailChallengeId
    registration_id: RegistrationId
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class EmailChallengeCompleted(DomainEvent):
    event_type = "email_challenge.completed"

    challenge_id: EmailChallengeId
    registration_id: RegistrationId
    completed_at: datetime
