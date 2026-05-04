from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FeatureCode:
    """Value object representing a feature code."""

    value: str

    def __post_init__(self):
        normalized_value = self.value.strip()
        if not normalized_value:
            raise ValueError("Feature code cannot be empty.")

        object.__setattr__(self, "value", normalized_value)

    def __str__(self):
        return self.value
