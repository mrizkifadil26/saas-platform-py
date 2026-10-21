from dataclasses import dataclass

from iam.shared.kernel.entity_id import EntityId
from iam.shared.kernel.value_object import ValueObject


@dataclass(frozen=True, slots=True)
class ExternalIdentityId(EntityId):
    pass


@dataclass(frozen=True, slots=True)
class ProviderSubject(ValueObject[str]):
    pass
