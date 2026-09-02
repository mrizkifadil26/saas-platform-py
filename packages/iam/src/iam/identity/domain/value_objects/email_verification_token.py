from __future__ import annotations

from dataclasses import dataclass

from iam.shared.domain.exceptions import ValidationError
from iam.shared.domain.value_object import ValueObject


@dataclass(frozen=True, slots=True)
class EmailVerificationToken(ValueObject[str]):
    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValidationError("Verification token cannot be empty")

        object.__setattr__(self, "value", normalized)
