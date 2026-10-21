from dataclasses import dataclass

from iam.registration.domain.value_objects import RegistrationId
from iam.shared.domain.email import EmailAddress


@dataclass(frozen=True, slots=True)
class EmailChallengeThrottleContext:
    email: EmailAddress
    ip_address: str
    registration_id: RegistrationId | None = None
