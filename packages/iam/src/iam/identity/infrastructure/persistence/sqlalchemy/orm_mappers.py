from iam.identity.domain import (
    EmailVerification,
    User,
    UserStatus,
)
from iam.identity.domain.credential import Credential
from iam.identity.domain.enums import CredentialStatus
from iam.identity.domain.value_objects import (
    CredentialId,
    EmailAddress,
    EmailVerificationId,
    EmailVerificationTokenHash,
    PasswordHash,
    UserId,
)

from .models import CredentialModel, EmailVerificationModel, UserModel


class UserORMMapper:
    @staticmethod
    def to_domain(model: UserModel) -> User:
        return User(
            id=UserId(model.id),
            email=EmailAddress(model.email),
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


class EmailVerificationORMMapper:
    @staticmethod
    def to_domain(model: EmailVerificationModel) -> EmailVerification:
        return EmailVerification(
            id=EmailVerificationId(model.id),
            user_id=UserId(model.user_id),
            token_hash=EmailVerificationTokenHash(model.token_hash),
            expires_at=model.expires_at,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: EmailVerification) -> EmailVerificationModel:
        return EmailVerificationModel(
            id=entity.id.value,
            user_id=entity.user_id.value,
            token_hash=entity.token_hash.value,
            expires_at=entity.expires_at,
            created_at=entity.created_at,
        )

    @staticmethod
    def update_model(
        model: EmailVerificationModel,
        entity: EmailVerification,
    ) -> None:
        model.user_id = entity.user_id.value
        model.token_hash = entity.token_hash.value
        model.expires_at = entity.expires_at
        model.created_at = entity.created_at


class CredentialORMMapper:
    @staticmethod
    def to_domain(model: CredentialModel) -> Credential:
        return Credential(
            id=CredentialId(model.id),
            user_id=UserId(model.user_id),
            password_hash=PasswordHash(model.password_hash),
            status=CredentialStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(credential: Credential) -> CredentialModel:
        return CredentialModel(
            id=credential.id.value,
            user_id=credential.user_id.value,
            password_hash=credential.password_hash.value,
            status=credential.status.value,
            created_at=credential.created_at,
            updated_at=credential.updated_at,
        )

    @staticmethod
    def update_model(
        model: CredentialModel,
        credential: Credential,
    ) -> None:
        model.user_id = credential.user_id.value
        model.password_hash = credential.password_hash.value
        model.status = credential.status.value
        model.created_at = credential.created_at
        model.updated_at = credential.updated_at
