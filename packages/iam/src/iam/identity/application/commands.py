from dataclasses import dataclass

from iam.identity.domain.value_objects import EmailAddress


@dataclass(frozen=True, slots=True)
class RegisterUserCommand:
    email: EmailAddress