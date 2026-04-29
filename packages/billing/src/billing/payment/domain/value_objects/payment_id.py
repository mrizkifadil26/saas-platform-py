from dataclasses import dataclass

from billing.shared.domain.value_objects.base_id import BaseId


@dataclass(frozen=True, slots=True)
class PaymentId(BaseId):
    """Value object representing a payment ID."""

    pass
