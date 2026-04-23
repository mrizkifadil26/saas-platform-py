from dataclasses import dataclass

from billing.shared.domain.value_objects.base_id import BaseId


@dataclass(frozen=True, slots=True)
class UserId(BaseId):
    pass
