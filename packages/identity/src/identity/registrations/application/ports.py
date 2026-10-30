from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from identity.accounts.domain.value_objects import UserId
from identity.registrations.application.dto import RegistrationContext
from identity.registrations.domain import EmailChallenge, EmailChallengePurpose, Registration
from identity.registrations.domain.value_objects import (
    EmailChallengeId,
    EmailChallengeToken,
    EmailChallengeTokenHash,
    RegistrationId,
    ResumeToken,
    ResumeTokenHash,
)
from identity.registrations.domain.workflow import RegistrationWorkflow
from identity.shared.domain.email import EmailAddress


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


class RegistrationWorkflowRepository(Protocol):
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

    async def find_by_registration_id(
        self,
        registration_id: RegistrationId,
    ) -> RegistrationWorkflow | None: ...

    async def find_by_registration_id_for_update(
        self,
        registration_id: RegistrationId,
    ) -> RegistrationWorkflow | None: ...

    async def find_by_resume_token_hash_for_update(
        self,
        token_hash: ResumeTokenHash,
    ) -> RegistrationWorkflow | None: ...


class EmailChallengeRepository(Protocol):
    async def add(
        self,
        challenge: EmailChallenge,
    ) -> None: ...

    async def find_by_id(
        self,
        challenge_id: EmailChallengeId,
    ) -> EmailChallenge | None: ...

    async def find_by_id_for_update(
        self,
        challenge_id: EmailChallengeId,
    ) -> EmailChallenge | None: ...

    async def find_active_for_update(
        self,
        challenge_id: EmailChallengeId,
        *,
        purpose: EmailChallengePurpose,
        now: datetime,
    ) -> EmailChallenge | None: ...

    async def find_by_token_hash_for_update(
        self,
        token_hash: EmailChallengeTokenHash,
    ) -> EmailChallenge | None: ...


@dataclass(frozen=True, slots=True)
class EmailRegistrationLookup:
    user_id: UserId | None
    registration: Registration | None
    workflow: RegistrationWorkflow | None

    @property
    def user_exists(self) -> bool:
        return self.user_id is not None

    @property
    def has_active_registration(self) -> bool:
        return self.registration is not None


class RegistrationLookup(Protocol):
    async def find_by_email(
        self,
        email: EmailAddress,
        *,
        now: datetime,
    ) -> EmailRegistrationLookup: ...


@dataclass(slots=True)
class StartedRegistration:
    context: RegistrationContext
    resume_token: ResumeToken
    challenge_token: EmailChallengeToken
