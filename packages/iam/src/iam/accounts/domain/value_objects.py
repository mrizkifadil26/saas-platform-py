from dataclasses import dataclass

from iam.shared.kernel.entity_id import EntityId


@dataclass(frozen=True, slots=True)
class UserId(EntityId):
    pass
