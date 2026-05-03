from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlanCode:
    """Value object representing a subscription plan code."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError(f"{self.__class__.__name__} must be a string")

        value = self.value.strip()

        if not value:
            raise ValueError(f"{self.__class__.__name__} cannot be empty")

        object.__setattr__(self, "value", value)

    def __str__(self) -> str:
        return self.value
