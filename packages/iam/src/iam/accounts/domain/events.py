from dataclasses import dataclass
from datetime import datetime

from iam.shared.domain.email import EmailAddress
from iam.shared.kernel.events import DomainEvent

from .value_objects import UserId

# @dataclass(frozen=True, slots=True)
# class UserRegistered(DomainEvent):
#     user_id: UserId
#     email: Email

#     event_type = "iam.user.registered"


@dataclass(frozen=True, slots=True)
class UserEmailVerified(DomainEvent):
    user_id: UserId
    verified_at: datetime


@dataclass(frozen=True, slots=True)
class UserActivated(DomainEvent):
    user_id: UserId
    activated_at: datetime


@dataclass(frozen=True, slots=True)
class UserDisabled(DomainEvent):
    user_id: UserId
    disabled_at: datetime


@dataclass(frozen=True, slots=True)
class UserLocked(DomainEvent):
    user_id: UserId
    locked_at: datetime


@dataclass(frozen=True, slots=True)
class UserUnlocked(DomainEvent):
    user_id: UserId
    unlocked_at: datetime


@dataclass(frozen=True, slots=True)
class UserSuspended(DomainEvent):
    user_id: UserId
    suspended_at: datetime


@dataclass(frozen=True, slots=True)
class UserUnsuspended(DomainEvent):
    user_id: UserId
    unsuspended_at: datetime


@dataclass(frozen=True, slots=True)
class UserEmailChanged(DomainEvent):
    user_id: UserId
    previous_email: EmailAddress
    new_email: EmailAddress
    changed_at: datetime
