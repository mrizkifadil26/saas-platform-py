from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PasswordConfig:
    time_cost: int = 3
    memory_cost: int = 65536
    parallelism: int = 4