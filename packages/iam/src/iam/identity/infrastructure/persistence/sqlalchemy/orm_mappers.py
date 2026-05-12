from iam.identity.domain import (
    User,
    UserStatus,
)
from iam.identity.domain.value_objects import EmailAddress, EmailVerification, UserId

from .models import UserModel


class UserORMMapper:
    @staticmethod
    def to_domain(model: UserModel) -> User:
        return User(
            id=UserId(model.id),
            email=EmailAddress(model.email),
            verification=EmailVerification(
                verified_at=model.email_verified_at,
                verification_requested_at=model.email_verification_requested_at,
            ),
            status=UserStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login_at=model.last_login_at,
        )

    @staticmethod
    def to_model(user: User) -> UserModel:
        return UserModel(
            id=user.id.value,
            email=user.email.value,
            email_verified_at=user.verification.verified_at,
            email_verification_requested_at=user.verification.verification_requested_at,
            status=user.status.value,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at,
        )

    @staticmethod
    def update_model(
        model: UserModel,
        user: User,
    ) -> None:
        model.email = user.email.value
        model.email_verified_at = user.verification.verified_at
        model.email_verification_requested_at = (
            user.verification.verification_requested_at
        )
        model.status = user.status
        model.created_at = user.created_at
        model.updated_at = user.updated_at
        model.last_login_at = user.last_login_at
