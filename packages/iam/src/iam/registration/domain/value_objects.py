from dataclasses import dataclass

from iam.shared.kernel.entity_id import EntityId
from iam.shared.kernel.exceptions import ValidationError
from iam.shared.kernel.value_object import ValueObject


@dataclass(frozen=True, slots=True)
class RegistrationId(EntityId):
    pass


@dataclass(frozen=True, slots=True)
class ResumeToken(ValueObject[str]):
    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValidationError("Resume token cannot be empty")

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class ResumeTokenHash(ValueObject[str]):
    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValidationError("Resume token hash cannot be empty")

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class EmailChallengeId(EntityId):
    pass


@dataclass(frozen=True, slots=True)
class EmailChallengeToken(ValueObject[str]):
    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValidationError("Verification token cannot be empty")

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class EmailChallengeTokenHash(ValueObject[str]):
    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValidationError("Verification token hash cannot be empty")

        object.__setattr__(self, "value", normalized)
