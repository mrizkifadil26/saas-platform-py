from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserDTO:
    id: str
    email: str
    status: str


@dataclass(frozen=True, slots=True)
class PaginatedUsersDTO:
    items: list[UserDTO]
    limit: int
    offset: int
    total: int
