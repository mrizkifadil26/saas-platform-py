from dataclasses import dataclass

from iam.shared.domain.events import DomainEvent

from .value_objects import UserId


@dataclass(frozen=True)
class UserRegistered(DomainEvent):
    user_id: UserId
    email: str


@dataclass(frozen=True)
class UserEmailVerified(DomainEvent):
    user_id: UserId


@dataclass(frozen=True)
class UserDisabled(DomainEvent):
    user_id: UserId
