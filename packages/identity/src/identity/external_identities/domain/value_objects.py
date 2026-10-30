from dataclasses import dataclass

from identity.shared.kernel.entity_id import EntityId
from identity.shared.kernel.value_object import ValueObject


@dataclass(frozen=True, slots=True)
class ExternalIdentityId(EntityId):
    pass


@dataclass(frozen=True, slots=True)
class ProviderSubject(ValueObject[str]):
    pass
