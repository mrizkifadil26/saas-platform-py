from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PageParams:
    limit: int = 50
    offset: int = 0

    def __post_init__(self) -> None:
        if self.limit <= 0:
            raise ValueError("limit must be greater than zero")
        if self.offset < 0:
            raise ValueError("offset cannot be negative")
