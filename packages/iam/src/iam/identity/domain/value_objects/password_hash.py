from dataclasses import dataclass

from iam.shared.domain.value_object import ValueObject


@dataclass(frozen=True, slots=True)
class PasswordHash(ValueObject):
    value: str
