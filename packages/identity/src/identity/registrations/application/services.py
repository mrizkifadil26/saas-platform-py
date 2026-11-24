import secrets
from dataclasses import dataclass

from identity.registrations.application.ports import (
    RegistrationRepository,
)
from identity.registrations.domain.value_objects import (
    EmailChallengeCode,
    EmailChallengeCodeHash,
    EmailChallengeToken,
    EmailChallengeTokenHash,
    ResumeToken,
    ResumeTokenHash,
)
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
class EmailChallengeCodeService:
    hasher: TokenHasher
    clock: Clock

    def issue(self) -> tuple[EmailChallengeCode, EmailChallengeCodeHash]:
        value = f"{secrets.randbelow(1_000_000):06d}"
        code = EmailChallengeCode(value)
        code_hash = self.hash(code)

        return code, code_hash

    def hash(
        self,
        code: EmailChallengeCode,
    ) -> EmailChallengeCodeHash:
        return EmailChallengeCodeHash(
            self.hasher.hash(code.value),
        )

    def verify(
        self,
        code: EmailChallengeCode,
        code_hash: EmailChallengeCodeHash,
    ) -> bool:
        return self.hasher.verify(
            code_hash.value,
            code.value,
        )


@dataclass(slots=True)
class RegistrationAccessService:
    registrations: RegistrationRepository

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
