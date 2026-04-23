from dataclasses import dataclass

from billing.domain.value_objects.base_id import BaseId


@dataclass(frozen=True, slots=True)
class FeatureCode(BaseId):
    """Value object representing a feature code."""

    pass
