from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PackCode:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("PackCode cannot be blank")
