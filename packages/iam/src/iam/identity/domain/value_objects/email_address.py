import re
from dataclasses import dataclass

from iam.shared.domain.exceptions import ValidationError
from iam.shared.domain.value_object import ValueObject

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_EMAIL_LENGTH = 320


@dataclass(frozen=True, slots=True)
class EmailAddress(ValueObject[str]):
    value: str

    def __post_init__(self) -> None:
        value = self.value.strip().lower()

        if not value:
            raise ValidationError("Email address cannot be empty")

        if len(value) > MAX_EMAIL_LENGTH:
            raise ValidationError("Email address too long")

        if not EMAIL_RE.fullmatch(value):
            raise ValidationError("Invalid email address format")

        local_part, _, domain_part = value.partition("@")

        if len(local_part) > 64:
            raise ValidationError("Email local part exceeds maximum length")

        if len(domain_part) > 255:
            raise ValidationError("Email domain exceeds maximum length")

        object.__setattr__(self, "value", value)
