from dataclasses import dataclass

from iam.registration.domain.value_objects import (
    EmailChallengeToken,
    EmailChallengeTokenHash,
    ResumeToken,
    ResumeTokenHash,
)
from iam.shared.application.throttling.throttler import Throttler
from iam.shared.infrastructure.security.tokens import SecureTokenGenerator, TokenHasher
from iam.shared.infrastructure.time.clock import Clock

from .throttling import EmailChallengeThrottleContext
from .throttling.policies import (
    RESEND_EMAIL_VERIFICATION_THROTTLE,
    START_EMAIL_REGISTRATION_THROTTLE,
)


@dataclass(slots=True)
class EmailChallengeService:
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
class RegistrationResumeTokenService:
    generator: SecureTokenGenerator
    hasher: TokenHasher

    def issue(self) -> tuple[ResumeToken, ResumeTokenHash]:
        raw_token = self.generator.generate()
        token_hash = self.hasher.hash(raw_token)

        return (
            ResumeToken(raw_token),
            ResumeTokenHash(token_hash),
        )

    def verify(
        self,
        token: ResumeToken,
        token_hash: ResumeTokenHash,
    ) -> bool:
        return self.hasher.verify(
            token.value,
            token_hash.value,
        )


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
