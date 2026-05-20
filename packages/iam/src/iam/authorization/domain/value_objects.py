from dataclasses import dataclass

from iam.shared.domain import EntityId, ValueObject


@dataclass(frozen=True, slots=True)
class RoleId(EntityId):
    pass


@dataclass(frozen=True, slots=True)
class Permission(ValueObject[str]):
    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Permission cannot be empty")

        if " " in self.value:
            raise ValueError("Permission cannot contain spaces")
