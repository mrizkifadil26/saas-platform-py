from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from iam.accounts.application.ports import UserRepository
from iam.accounts.application.services import AccountService
from iam.registration.domain import (
    EmailChallenge,
    EmailChallengePurpose,
    Registration,
    RegistrationMethod,
)
from iam.registration.domain.exceptions import (
    RegistrationEmailAlreadyVerifiedError,
    RegistrationNotFoundError,
)
from iam.registration.domain.value_objects import EmailChallengeToken, ResumeToken
from iam.shared.application.command_bus import CommandHandler
from iam.shared.domain.email import EmailAddress
from iam.shared.infrastructure.outbox import OutboxWriter
from iam.shared.infrastructure.outbox.message import OutboxMessage, OutboxMessageFactory
from iam.shared.infrastructure.security.password import PasswordHasher, PasswordPolicy
from iam.shared.infrastructure.time import Clock

from .commands import (
    CancelRegistration,
    CompleteEmailRegistration,
    ResendEmailVerification,
    SetRegistrationPassword,
    StartEmailRegistration,
    VerifyRegistrationEmail,
)
from .dto import (
    EmailVerificationResult,
    PasswordSet,
    RegistrationCancelled,
    RegistrationStarted,
    RegistrationView,
)
from .exceptions import (
    EmailChallengeInvalidTokenError,
    RegistrationEmailAlreadyRegisteredError,
    RegistrationResumeTokenInvalidError,
    RegistrationResumeTokenRequiredError,
)
from .ports import EmailChallengeRepository, RegistrationRepository
from .services import (
    EmailChallengeService,
    EmailChallengeThrottler,
    RegistrationResumeTokenService,
)
from .throttling import EmailChallengeThrottleContext

REGISTRATION_TTL = timedelta(hours=24)
VERIFICATION_TTL = timedelta(minutes=30)


@dataclass(slots=True)
class StartEmailRegistrationHandler(
    CommandHandler[
        StartEmailRegistration,
        RegistrationStarted,
    ]
):
    registrations: RegistrationRepository
    users: UserRepository
    challenges: EmailChallengeRepository

    email_challenge: EmailChallengeService
    resume_tokens: RegistrationResumeTokenService

    throttler: EmailChallengeThrottler

    outbox: OutboxWriter
    outbox_factory: OutboxMessageFactory

    db_session: AsyncSession
    clock: Clock

    async def __call__(
        self,
        command: StartEmailRegistration,
    ) -> RegistrationStarted:
        now = self.clock.now()
        email = EmailAddress(command.email)

        async with self.db_session.begin():
            user = await self.users.find_by_email(email)
            if user is not None:
                # TODO: Catch this to re-route
                raise RegistrationEmailAlreadyRegisteredError()

            registration = await self.registrations.find_active_by_email(
                email,
                now=now,
            )

            if registration is not None:
                if command.resume_token is None:
                    raise RegistrationResumeTokenRequiredError()

                if not self.resume_tokens.verify(
                    command.resume_token,
                    registration.resume_token_hash,
                ):
                    raise RegistrationResumeTokenInvalidError()

                return RegistrationStarted(
                    registration_id=registration.id,
                    method=registration.method,
                    step=registration.step,
                    expires_at=registration.expires_at,
                    resume_token=None,
                )

            resume_token, resume_token_hash = self.resume_tokens.issue()

            registration = Registration.create(
                method=RegistrationMethod.EMAIL,
                email=email,
                resume_token_hash=resume_token_hash,
                expires_at=now + REGISTRATION_TTL,
                created_at=now,
                updated_at=now,
            )

            challenge_token, challenge_token_hash = self.email_challenge.issue()

            challenge = EmailChallenge.create(
                registration_id=registration.id,
                purpose=EmailChallengePurpose.EMAIL_VERIFICATION,
                token_hash=challenge_token_hash,
                created_at=now,
                expires_at=now + VERIFICATION_TTL,
            )

            await self.registrations.add(registration)
            await self.challenges.add(challenge)

            events = challenge.pull_events()
            await self.outbox.add_events(events)
            await self.outbox.add(
                OutboxMessage(
                    id=uuid4(),
                    message_type="email.verification.send",
                    payload={
                        "registration_id": str(registration.id),
                        "challenge_id": str(challenge.id),
                        "email": email.value,
                        "token": challenge_token,
                    },
                    occurred_at=now,
                )
            )

        return RegistrationStarted(
            registration_id=registration.id,
            method=registration.method,
            step=registration.step,
            expires_at=registration.expires_at,
            resume_token=resume_token,
        )


@dataclass(slots=True)
class VerifyRegistrationEmailHandler(
    CommandHandler[
        VerifyRegistrationEmail,
        EmailVerificationResult,
    ]
):
    registrations: RegistrationRepository
    challenges: EmailChallengeRepository

    email_challenge: EmailChallengeService

    db_session: AsyncSession
    clock: Clock

    async def __call__(
        self,
        command: VerifyRegistrationEmail,
    ) -> EmailVerificationResult:
        now = self.clock.now()

        async with self.db_session.begin():
            registration = await self.registrations.find_by_id_for_update(
                command.registration_id,
            )

            if registration is None:
                raise RegistrationNotFoundError(
                    command.registration_id,
                )

            if registration.email_verified:
                return EmailVerificationResult(
                    registration=RegistrationView.from_result(registration),
                )

            challenge = await self.challenges.get_active_for_registration(
                registration.id,
                now=now,
            )
            if challenge is None:
                raise EmailChallengeInvalidTokenError()

            self.email_challenge.verify(
                token=EmailChallengeToken(command.challenge_token),
                token_hash=challenge.token_hash,
            )

            challenge.complete(completed_at=now)
            registration.verify_email(now=now)

            await self.challenges.update(challenge)
            await self.registrations.update(registration)

        return EmailVerificationResult(
            registration=RegistrationView.from_result(registration),
        )


@dataclass(slots=True)
class SetRegistrationPasswordHandler(
    CommandHandler[
        SetRegistrationPassword,
        PasswordSet,
    ]
):
    registrations: RegistrationRepository

    password_policy: PasswordPolicy
    password_hasher: PasswordHasher

    resume_tokens: RegistrationResumeTokenService

    db_session: AsyncSession
    clock: Clock

    async def __call__(
        self,
        command: SetRegistrationPassword,
    ) -> PasswordSet:
        now = self.clock.now()

        async with self.db_session.begin():
            registration = await self.registrations.find_by_id_for_update(
                command.registration_id,
            )

            if registration is None:
                raise RegistrationNotFoundError(
                    command.registration_id,
                )

            if not self.resume_tokens.verify(
                command.resume_token,
                registration.resume_token_hash,
            ):
                raise RegistrationResumeTokenInvalidError()

            self.password_policy.validate(command.password)

            password_hash = self.password_hasher.hash(command.password)
            registration.set_password(
                password_hash=password_hash,
                now=now,
            )

            await self.registrations.update(registration)

        return PasswordSet(
            registration=RegistrationView.from_result(registration),
        )


@dataclass(slots=True)
class ResendEmailVerificationHandler(
    CommandHandler[
        ResendEmailVerification,
        None,
    ]
):
    registrations: RegistrationRepository
    challenges: EmailChallengeRepository

    email_challenge: EmailChallengeService
    resume_tokens: RegistrationResumeTokenService
    throttler: EmailChallengeThrottler

    outbox: OutboxWriter
    db_session: AsyncSession
    clock: Clock

    async def __call__(
        self,
        command: ResendEmailVerification,
    ) -> None:
        now = self.clock.now()

        async with self.db_session.begin():
            registration = await self.registrations.find_by_id_for_update(
                command.registration_id,
            )

            if registration is None:
                raise RegistrationNotFoundError(
                    command.registration_id,
                )

            # No point sending another verification email.
            registration.ensure_pending(now=now)

            if registration.email_verified:
                raise RegistrationEmailAlreadyVerifiedError(
                    registration.id,
                )

            if command.resume_token is None:
                raise RegistrationResumeTokenRequiredError()

            if not self.resume_tokens.verify(
                command.resume_token,
                registration.resume_token_hash,
            ):
                raise RegistrationResumeTokenInvalidError()

            # Prevent "send again" spam.
            email = registration.require_email()
            await self.throttler.enforce_resend(
                context=EmailChallengeThrottleContext(
                    email=email,
                    ip_address=command.ip_address,
                    registration_id=registration.id,
                )
            )

            # Invalidate the previous challenge.
            active_challenge = await self.challenges.get_active_for_registration(
                registration.id,
                now=now,
            )

            if active_challenge is not None:
                active_challenge.revoke(revoked_at=now)
                await self.challenges.update(active_challenge)

            challenge_token, challenge_token_hash = self.email_challenge.issue()

            challenge = EmailChallenge.create(
                registration_id=registration.id,
                purpose=EmailChallengePurpose.EMAIL_VERIFICATION,
                token_hash=challenge_token_hash,
                created_at=now,
                expires_at=now + VERIFICATION_TTL,
            )

            await self.challenges.add(challenge)

            await self.outbox.add_events(challenge.pull_events())
            await self.outbox.add(
                OutboxMessage(
                    id=uuid4(),
                    message_type="email.verification.send",
                    payload={
                        "registration_id": str(registration.id),
                        "challenge_id": str(challenge.id),
                        "email": email.value,
                        "token": challenge_token,
                    },
                    occurred_at=now,
                )
            )


@dataclass(slots=True)
class CompleteRegistrationHandler(
    CommandHandler[
        CompleteEmailRegistration,
        RegistrationView,
    ]
):
    registrations: RegistrationRepository

    accounts: AccountService

    db_session: AsyncSession
    clock: Clock

    async def __call__(
        self,
        command: CompleteEmailRegistration,
    ) -> RegistrationView:
        now = self.clock.now()

        async with self.db_session.begin():
            registration = await self.registrations.find_by_id_for_update(
                command.registration_id,
            )

            if registration is None:
                raise RegistrationNotFoundError(
                    command.registration_id,
                )

            if registration.is_completed:
                return RegistrationView.from_result(registration)

            user_id = await self.accounts.create_user(
                email=registration.require_email(),
                email_verified_at=registration.email_verified_at,
                created_at=now,
            )

            # user = await users.create_from_registration(registration)
            registration.complete(
                user_id=user_id,
                completed_at=now,
            )

            await self.registrations.update(registration)

        return RegistrationView.from_result(registration)


@dataclass(slots=True)
class CancelRegistrationHandler(
    CommandHandler[
        CancelRegistration,
        RegistrationCancelled,
    ],
):
    registrations: RegistrationRepository
    resume_tokens: RegistrationResumeTokenService

    db_session: AsyncSession
    clock: Clock

    async def __call__(
        self,
        command: CancelRegistration,
    ) -> RegistrationCancelled:
        now = self.clock.now()

        async with self.db_session.begin():
            registration = await self.registrations.find_by_id_for_update(
                command.registration_id,
            )

            if registration is None:
                raise RegistrationNotFoundError(
                    command.registration_id,
                )

            if not self.resume_tokens.verify(
                ResumeToken(command.resume_token),
                registration.resume_token_hash,
            ):
                raise RegistrationResumeTokenInvalidError()

            registration.cancel(cancelled_at=now)

            await self.registrations.update(registration)

        return RegistrationCancelled(
            registration=RegistrationView.from_result(registration),
        )
