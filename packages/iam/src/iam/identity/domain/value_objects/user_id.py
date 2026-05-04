from dataclasses import dataclass

from iam.shared.domain.value_object import UUIDIdentifier


@dataclass(frozen=True, slots=True)
class UserId(UUIDIdentifier):
    pass
