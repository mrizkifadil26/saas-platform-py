from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlanCode:
    value: str

    def __post_init__(self):
        normalized_value = self.value.strip()
        if not normalized_value:
            raise ValueError("PlanCode cannot be empty")

        object.__setattr__(self, "value", normalized_value)

    def __str__(self) -> str:
        return self.value
