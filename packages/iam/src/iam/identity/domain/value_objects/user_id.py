from dataclasses import dataclass

from iam.shared.domain import EntityId


@dataclass(frozen=True, slots=True)
class UserId(EntityId):
    pass
