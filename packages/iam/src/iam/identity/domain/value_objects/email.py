import re
from dataclasses import dataclass

from iam.shared.domain import ValueObject
from iam.shared.domain.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class Email(ValueObject[str]):
    MAX_LENGTH = 320
    PATTERN = re.compile(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )

    def __post_init__(self) -> None:
        value = self.value.strip().lower()

        if not value:
            raise ValidationError("Email address cannot be empty")

        if len(value) > self.MAX_LENGTH:
            raise ValidationError("Email address too long")

        if not self.PATTERN.fullmatch(value):
            raise ValidationError("Invalid email address format")

        local_part, _, domain_part = value.partition("@")

        if len(local_part) > 64:
            raise ValidationError("Email local part exceeds maximum length")

        if len(domain_part) > 255:
            raise ValidationError("Email domain exceeds maximum length")

        object.__setattr__(self, "value", value)
