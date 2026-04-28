from __future__ import annotations

from dataclasses import dataclass


# TODO: should this inherit from BaseId? or should it be a separate value object?
@dataclass(frozen=True, slots=True)
class PricingKey:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Pricing key is required")

        if self.value.strip() != self.value:
            raise ValueError("Pricing key cannot contain leading or trailing spaces")

        if " " in self.value:
            raise ValueError("Pricing key cannot contain spaces")

    def __str__(self) -> str:
        return self.value
