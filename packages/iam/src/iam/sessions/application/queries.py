from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValidateSessionQuery:
    token: str
