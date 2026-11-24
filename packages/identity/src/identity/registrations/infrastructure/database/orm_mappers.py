from identity.registrations.domain import EmailChallenge
from identity.registrations.domain.enums import EmailChallengePurpose
from identity.registrations.domain.value_objects import (
    EmailChallengeId,
    EmailChallengeTokenHash,
    RegistrationId,
)
from identity.shared.domain.email import EmailAddress

from .models import EmailChallengeModel


class EmailChallengeORMMapper:
    @staticmethod
    def to_domain(model: EmailChallengeModel) -> EmailChallenge:
        return EmailChallenge(
            id=EmailChallengeId(model.id),
            registration_id=RegistrationId(model.registration_id),
            email=EmailAddress(model.email),
            purpose=EmailChallengePurpose(model.purpose),
            token_hash=EmailChallengeTokenHash(model.token_hash),
            created_at=model.created_at,
            expires_at=model.expires_at,
            completed_at=model.completed_at,
            revoked_at=model.revoked_at,
        )

    @staticmethod
    def to_model(entity: EmailChallenge) -> EmailChallengeModel:
        return EmailChallengeModel(
            id=entity.id.value,
            registration_id=entity.registration_id.value,
            email=entity.email.value,
            token_hash=entity.token_hash.value,
            purpose=entity.purpose.value,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
            completed_at=entity.completed_at,
            revoked_at=entity.revoked_at,
        )

    @staticmethod
    def update_model(
        model: EmailChallengeModel,
        entity: EmailChallenge,
    ) -> None:
        model.id = entity.id.value
        model.registration_id = entity.registration_id.value
        model.email = entity.email.value
        model.token_hash = entity.token_hash.value
        model.purpose = entity.purpose.value
        model.created_at = entity.created_at
        model.expires_at = entity.expires_at
        model.completed_at = entity.completed_at
        model.revoked_at = entity.revoked_at
