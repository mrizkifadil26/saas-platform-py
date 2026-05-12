from dataclasses import dataclass

from iam.shared.domain import EntityId
from iam.shared.domain.entity_id import ValueObject
from iam.shared.domain.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class SessionId(EntityId):
    pass


@dataclass(frozen=True, slots=True)
class SessionToken(ValueObject[str]):
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValidationError("session token cannot be empty.")

        object.__setattr__(self, "value", normalized)
