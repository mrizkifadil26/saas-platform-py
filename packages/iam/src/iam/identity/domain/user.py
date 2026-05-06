from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from iam.identity.domain.user_events import UserDisabled, UserRegistered
from iam.identity.domain.user_status import UserStatus
from iam.identity.domain.value_objects.email_address import (
    EmailAddress,
)
from iam.identity.domain.value_objects.password_hash import (
    PasswordHash,
)
from iam.identity.domain.value_objects.user_id import UserId
from iam.shared.domain.aggregate_root import AggregateRoot
from iam.shared.domain.exceptions import ValidationError


@dataclass
class User(AggregateRoot[UserId]):
    email: EmailAddress
    password_hash: PasswordHash
    status: UserStatus

    @classmethod
    def register(
        cls,
        email: EmailAddress,
        password_hash: PasswordHash,
    ) -> User:
        user = cls(
            id=UserId(uuid4()),
            email=email,
            password_hash=password_hash,
            status=UserStatus.PENDING,
        )

        event = UserRegistered(
            user_id=user.id,
            email=email.value,
        )
        user.record_event(event)

        return user

    def activate(self) -> None:
        if self.status != UserStatus.PENDING:
            raise ValidationError("User already active or invalid state")

        self.status = UserStatus.ACTIVE

    def disable(self) -> None:
        if self.status != UserStatus.DISABLED:
            raise ValidationError("User already disabled or invalid state")

        self.status = UserStatus.DISABLED

        event = UserDisabled(user_id=self.id)
        self.record_event(event)

    def change_password(self, new_password_hash: PasswordHash) -> None:
        if self.status != UserStatus.ACTIVE:
            raise ValidationError("Cannot change password for inactive user")

        self.password_hash = new_password_hash
