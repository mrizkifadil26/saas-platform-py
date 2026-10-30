from dataclasses import dataclass

from identity.registration.domain.value_objects import RegistrationId
from identity.shared.domain.email import EmailAddress


@dataclass(frozen=True, slots=True)
class EmailChallengeThrottleContext:
    email: EmailAddress
    ip_address: str
    registration_id: RegistrationId | None = None
