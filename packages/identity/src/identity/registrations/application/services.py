from dataclasses import dataclass

from identity.registrations.application.exceptions import RegistrationResumeTokenInvalidError
from identity.registrations.application.ports import (
    RegistrationRepository,
    RegistrationWorkflowRepository,
)
from identity.registrations.domain.exceptions import RegistrationNotFoundError
from identity.registrations.domain.registration import Registration
from identity.registrations.domain.value_objects import (
    EmailChallengeToken,
    EmailChallengeTokenHash,
    ResumeToken,
    ResumeTokenHash,
)
from identity.registrations.domain.workflow import RegistrationWorkflow
from identity.shared.application.throttling.throttler import Throttler
from identity.shared.infrastructure.security.tokens import SecureTokenGenerator, TokenHasher
from identity.shared.infrastructure.time.clock import Clock

from .throttling import EmailChallengeThrottleContext
from .throttling.policies import (
    RESEND_EMAIL_VERIFICATION_THROTTLE,
    START_EMAIL_REGISTRATION_THROTTLE,
)


@dataclass(slots=True)
class EmailChallengeTokenService:
    generator: SecureTokenGenerator
    hasher: TokenHasher
    clock: Clock

    def issue(self) -> tuple[EmailChallengeToken, EmailChallengeTokenHash]:
        raw_token = self.generator.generate()
        token_hash = self.hasher.hash(raw_token)

        return (
            EmailChallengeToken(raw_token),
            EmailChallengeTokenHash(token_hash),
        )

    def hash(
        self,
        raw_token: EmailChallengeToken,
    ) -> EmailChallengeTokenHash:
        return EmailChallengeTokenHash(
            self.hasher.hash(raw_token.value),
        )

    def verify(
        self,
        token: EmailChallengeToken,
        token_hash: EmailChallengeTokenHash,
    ) -> bool:
        return self.hasher.verify(
            token.value,
            token_hash.value,
        )


@dataclass(slots=True)
class RegistrationAccessService:
    registrations: RegistrationRepository
    workflows: RegistrationWorkflowRepository

    generator: SecureTokenGenerator
    hasher: TokenHasher

    clock: Clock

    def issue(self) -> tuple[ResumeToken, ResumeTokenHash]:
        raw_token = self.generator.generate()
        token_hash = self.hasher.hash(raw_token)

        return (
            ResumeToken(raw_token),
            ResumeTokenHash(token_hash),
        )

    async def require(
        self,
        resume_token: ResumeToken,
    ) -> tuple[Registration, RegistrationWorkflow]:
        token_hash = ResumeTokenHash(
            self.hasher.hash(resume_token.value),
        )

        workflow = await self.workflows.find_by_resume_token_hash_for_update(token_hash)
        if workflow is None:
            raise RegistrationResumeTokenInvalidError()

        now = self.clock.now()
        workflow.ensure_accessible(now=now)

        registration = await self.registrations.find_by_id(
            workflow.registration_id,
        )

        if registration is None:
            raise RegistrationNotFoundError()

        return registration, workflow


@dataclass(frozen=True, slots=True)
class EmailChallengeThrottleResult:
    retry_after: float | None


@dataclass(slots=True)
class EmailChallengeThrottler:
    throttler: Throttler

    async def enforce_start(
        self,
        context: EmailChallengeThrottleContext,
    ) -> None:
        await self.throttler.enforce(
            START_EMAIL_REGISTRATION_THROTTLE,
            context=context,
        )

    async def enforce_resend(
        self,
        context: EmailChallengeThrottleContext,
    ) -> None:
        await self.throttler.enforce(
            RESEND_EMAIL_VERIFICATION_THROTTLE,
            context=context,
        )
