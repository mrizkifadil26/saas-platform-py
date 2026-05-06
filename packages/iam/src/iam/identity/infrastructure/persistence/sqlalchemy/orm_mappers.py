from iam.identity.domain.user import User
from iam.identity.domain.user_status import UserStatus
from iam.identity.domain.value_objects.email_address import EmailAddress
from iam.identity.domain.value_objects.password_hash import PasswordHash
from iam.identity.domain.value_objects.user_id import UserId
from iam.identity.infrastructure.persistence.sqlalchemy.models import UserModel


class UserORMMapper:
    @staticmethod
    def to_domain(model: UserModel) -> User:
        return User(
            id=UserId(model.id),
            email=EmailAddress(model.email),
            password_hash=PasswordHash(model.password_hash),
            status=UserStatus(model.status),
        )

    @staticmethod
    def to_model(user: User) -> UserModel:
        return UserModel(
            id=user.id.value,
            email=user.email.value,
            password_hash=user.password_hash.value,
            status=user.status.value,
        )

    @staticmethod
    def update_model(
        model: UserModel,
        user: User,
    ) -> None:
        model.email = user.email.value
        model.password_hash = user.password_hash.value
        model.status = user.status.value
