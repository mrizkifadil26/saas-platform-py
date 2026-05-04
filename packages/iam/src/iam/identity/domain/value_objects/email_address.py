from dataclasses import dataclass

from iam.shared.domain.exceptions import ValidationError
from iam.shared.domain.value_object import ValueObject


@dataclass(frozen=True, slots=True)
class EmailAddress(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValidationError("Email address cannot be empty")

        if "@" not in self.value or self.value.count("@") != 1:
            raise ValidationError("Invalid email address format")

        object.__setattr__(self, "value", self.value.lower())

    def __str__(self) -> str:
        return self.value
