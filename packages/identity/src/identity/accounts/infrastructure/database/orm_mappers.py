from identity.accounts.domain import (
    User,
    UserStatus,
)
from identity.accounts.domain.value_objects import (
    UserId,
)

from .models import UserModel


class UserORMMapper:
    @staticmethod
    def to_domain(model: UserModel) -> User:
        return User(
            id=UserId(model.id),
            email=Email(model.email),
            status=UserStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            email_verified_at=model.email_verified_at,
            last_login_at=model.last_login_at,
        )

    @staticmethod
    def to_model(user: User) -> UserModel:
        return UserModel(
            id=user.id.value,
            email=user.email.value,
            status=user.status.value,
            created_at=user.created_at,
            updated_at=user.updated_at,
            email_verified_at=user.email_verified_at,
            last_login_at=user.last_login_at,
        )

    @staticmethod
    def update_model(
        model: UserModel,
        user: User,
    ) -> None:
        model.email = user.email.value
        model.status = user.status
        model.created_at = user.created_at
        model.updated_at = user.updated_at
        model.email_verified_at = user.email_verified_at
        model.last_login_at = user.last_login_at
