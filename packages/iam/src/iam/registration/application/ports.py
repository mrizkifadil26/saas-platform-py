from datetime import datetime
from typing import Protocol

from iam.registration.domain.email_challenge import EmailChallenge
from iam.registration.domain.registration import Registration
from iam.registration.domain.value_objects import (
    EmailChallengeId,
    EmailChallengeTokenHash,
    RegistrationId,
)
from iam.shared.domain.email import EmailAddress


class RegistrationRepository(Protocol):
    async def add(
        self,
        registration: Registration,
    ) -> None: ...

    async def update(
        self,
        registration: Registration,
    ) -> None: ...

    async def find_by_id(
        self,
        registration_id: RegistrationId,
    ) -> Registration | None: ...

    async def find_by_id_for_update(
        self,
        registration_id: RegistrationId,
    ) -> Registration | None: ...

    async def find_active_by_email(
        self,
        email: EmailAddress,
        *,
        now: datetime,
    ) -> Registration | None: ...


class EmailChallengeRepository(Protocol):
    async def add(
        self,
        challenge: EmailChallenge,
    ) -> None: ...

    async def update(
        self,
        challenge: EmailChallenge,
    ) -> None: ...

    async def find_by_id(
        self,
        challenge_id: EmailChallengeId,
    ) -> EmailChallenge | None: ...

    # async def find_by_user_id(
    #     self,
    #     user_id: UserId,
    # ) -> EmailChallenge | None: ...

    async def get_active_for_registration(
        self,
        registration_id: RegistrationId,
        *,
        now: datetime,
    ) -> EmailChallenge | None: ...

    async def find_active_token_hash_for_update(
        self,
        token_hash: EmailChallengeTokenHash,
    ) -> EmailChallenge | None: ...
