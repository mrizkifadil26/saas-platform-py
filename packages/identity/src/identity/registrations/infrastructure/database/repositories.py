from collections.abc import Sequence
from datetime import datetime

from identity.registrations.application.ports import EmailChallengeRepository
from identity.registrations.domain.email_challenge import EmailChallenge
from identity.registrations.domain.value_objects import (
    EmailChallengeId,
    EmailChallengeTokenHash,
    RegistrationId,
)


class SQLAlchemyEmailChallengeRepository(
    EmailChallengeRepository,
):
    async def add(self, challenge: EmailChallenge) -> None:
        raise NotImplementedError

    async def get(self, challenge_id: EmailChallengeId) -> EmailChallenge | None:
        raise NotImplementedError

    async def get_for_update(self, challenge_id: EmailChallengeId) -> EmailChallenge | None:
        raise NotImplementedError

    async def find_active(
        self, challenge_id: EmailChallengeId, *, now: datetime
    ) -> EmailChallenge | None:
        raise NotImplementedError

    async def find_by_token_hash(
        self, token_hash: EmailChallengeTokenHash
    ) -> EmailChallenge | None:
        raise NotImplementedError

    async def list_by_registration(
        self, registration_id: RegistrationId
    ) -> Sequence[EmailChallenge]:
        raise NotImplementedError

    async def remove(self, challenge_id: EmailChallengeId) -> None:
        raise NotImplementedError
