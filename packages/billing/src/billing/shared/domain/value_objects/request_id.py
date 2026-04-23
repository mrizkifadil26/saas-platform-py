from dataclasses import dataclass

from billing.shared.domain.value_objects.base_id import BaseId


@dataclass(frozen=True, slots=True)
class RequestId(BaseId):
    """Value object representing a request ID."""

    pass
