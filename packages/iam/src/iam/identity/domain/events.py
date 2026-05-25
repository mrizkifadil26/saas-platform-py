from dataclasses import dataclass
from datetime import datetime

from iam.shared.domain.events import DomainEvent

from .value_objects import Email, UserId


@dataclass(frozen=True, slots=True)
class UserRegistered(DomainEvent):
    user_id: UserId
    email: Email


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
    previous_email: Email
    new_email: Email
    changed_at: datetime
