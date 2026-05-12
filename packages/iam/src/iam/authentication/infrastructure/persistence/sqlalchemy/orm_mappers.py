from iam.authentication.domain import Credential, CredentialStatus
from iam.authentication.domain.value_objects import CredentialId, PasswordHash
from iam.identity.domain.value_objects import UserId

from .models import CredentialModel


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
