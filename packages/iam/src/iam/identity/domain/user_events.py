from dataclasses import dataclass

from iam.identity.domain.value_objects.user_id import UserId
from iam.shared.domain.domain_event import DomainEvent


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
