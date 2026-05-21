from dataclasses import dataclass

from iam.shared.domain import EntityId
from iam.shared.domain.entity_id import ValueObject
from iam.shared.domain.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class SessionId(EntityId):
    pass


@dataclass(frozen=True, slots=True)
class RefreshTokenId(EntityId):
    pass


@dataclass(frozen=True, slots=True)
class RefreshTokenHash(ValueObject[str]):
    value: str

    def __post_init__(self) -> None:
        value = self.value.strip()

        if not value:
            raise ValidationError("Refresh token hash cannot be empty")

        object.__setattr__(self, "value", value)

@dataclass(frozen=True, slots=True)
class RefreshTokenSecret(ValueObject[str]):
    value: str

    def __post_init__(self) -> None:
        value = self.value.strip()

        if not value:
            raise ValidationError("Refresh token hash cannot be empty")

        object.__setattr__(self, "value", value)
