from dataclasses import dataclass

from iam.identity.domain.value_objects.user_id import UserId
from iam.shared.application.command import Command


@dataclass(frozen=True, slots=True)
class RegisterUser(Command):
    email: str
    password: str


@dataclass(frozen=True, slots=True)
class ActivateUser(Command):
    user_id: UserId


@dataclass(frozen=True, slots=True)
class DeactivateUser(Command):
    user_id: UserId


@dataclass(frozen=True, slots=True)
class ChangePassword(Command):
    user_id: UserId
    new_password: str
