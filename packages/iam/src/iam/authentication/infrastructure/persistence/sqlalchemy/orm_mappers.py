from iam.authentication.domain import (
    AuthenticationAttempt,
    Credential,
    CredentialStatus,
)
from iam.authentication.domain.value_objects import (
    AuthenticationAttemptId,
    CredentialId,
    PasswordHash,
)
from iam.identity.domain.value_objects import Email, UserId

from .models import (
    AuthenticationAttemptModel,
    CredentialModel,
)


class CredentialORMMapper:
    @staticmethod
    def to_domain(model: CredentialModel) -> Credential:
        return Credential(
            id=CredentialId(model.id),
            user_id=UserId(model.user_id),
            type=model.type,
            secret_hash=PasswordHash(model.secret_hash),
            status=CredentialStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(credential: Credential) -> CredentialModel:
        return CredentialModel(
            id=credential.id.value,
            user_id=credential.user_id.value,
            secret_hash=credential.secret_hash.value,
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
        model.secret_hash = credential.secret_hash.value
        model.status = credential.status
        model.created_at = credential.created_at
        model.updated_at = credential.updated_at


class AuthenticationAttemptORMMapper:
    @staticmethod
    def to_domain(
        model: AuthenticationAttemptModel,
    ) -> AuthenticationAttempt:
        return AuthenticationAttempt(
            id=AuthenticationAttemptId(model.id),
            email=Email(model.email),
            user_id=(UserId(model.user_id) if model.user_id is not None else None),
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            outcome=model.outcome,
            denial_reason=model.denial_reason,
            attempted_at=model.attempted_at,
        )

    @staticmethod
    def to_model(
        entity: AuthenticationAttempt,
    ) -> AuthenticationAttemptModel:
        return AuthenticationAttemptModel(
            id=str(entity.id),
            email=str(entity.email),
            user_id=(str(entity.user_id) if entity.user_id is not None else None),
            ip_address=entity.ip_address,
            user_agent=entity.user_agent,
            outcome=entity.outcome,
            denial_reason=entity.denial_reason,
            attempted_at=entity.attempted_at,
        )
