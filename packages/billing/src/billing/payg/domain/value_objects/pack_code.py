from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PackCode:
    value: str

    def __post_init__(self) -> None:
        normalized_value = self.value.strip()
        if not normalized_value:
            raise ValueError("PackCode cannot be blank")

        object.__setattr__(self, "value", normalized_value)

    def __str__(self) -> str:
        return self.value
