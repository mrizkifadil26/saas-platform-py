from dataclasses import dataclass

from billing.shared.domain.value_objects.base_id import BaseId


@dataclass(frozen=True, slots=True)
class PaygPurchaseId(BaseId):
    """Value object representing the unique identifier for a Pay-as-you-go purchase."""

    pass
