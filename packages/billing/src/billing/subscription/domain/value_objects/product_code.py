from dataclasses import dataclass

from billing.shared.domain.value_objects.base_id import BaseId


@dataclass(frozen=True, slots=True)
class ProductCode:
    """Value object representing a product code."""

    value: str

    def __post_init__(self):
        normalized_value = self.value.strip()
        if not normalized_value:
            raise ValueError("Product code cannot be empty.")

        object.__setattr__(self, "value", normalized_value)

    def __str__(self):
        return self.value
