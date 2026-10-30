from dataclasses import dataclass

from identity.shared.kernel.entity_id import EntityId


@dataclass(frozen=True, slots=True)
class CredentialId(EntityId):
    pass
