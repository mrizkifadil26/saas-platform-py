from dataclasses import dataclass

from billing.domain.value_objects.base_id import BaseId


@dataclass(frozen=True, slots=True)
class ProductCode(BaseId):
    """Value object representing a product code."""

    pass
