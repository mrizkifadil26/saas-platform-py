from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from identity.accounts.application.ports import UserRepository
from identity.accounts.application.services import AccountService
from identity.registrations.domain import (
    EmailChallenge,
    EmailChallengePurpose,
    Registration,
    RegistrationMethod,
)
from identity.registrations.domain.exceptions import (
    RegistrationEmailAlreadyVerifiedError,
    RegistrationNotFoundError,
)
from identity.registrations.domain.value_objects import EmailChallengeToken, ResumeToken
from identity.registrations.domain.workflow import RegistrationWorkflow
from identity.shared.application.command_bus import CommandHandler
from identity.shared.domain.email import EmailAddress
from identity.shared.infrastructure.outbox import OutboxWriter
from identity.shared.infrastructure.outbox.message import OutboxMessage, OutboxMessageFactory
from identity.shared.infrastructure.security.password import PasswordHasher, PasswordPolicy
from identity.shared.infrastructure.time import Clock

from .commands import (
    BeginEmailRegistration,
    CancelRegistration,
    CompleteEmailRegistration,
    ResendEmailVerification,
    SetRegistrationPassword,
    VerifyRegistrationEmail,
)
from .dto import (
    EmailRegistrationStarted,
    EmailVerificationResult,
    PasswordSet,
    RegistrationCancelled,
    RegistrationView,
)
from .exceptions import (
    EmailChallengeInvalidTokenError,
    RegistrationResumeTokenInvalidError,
    RegistrationResumeTokenRequiredError,
)
from .ports import (
    EmailChallengeRepository,
    RegistrationLookup,
    RegistrationRepository,
    RegistrationWorkflowRepository,
)
from .services import (
    EmailChallengeThrottler,
    EmailChallengeTokenService,
    RegistrationAccessService,
    RegistrationResumeTokenService,
)
from .throttling import EmailChallengeThrottleContext

REGISTRATION_TTL = timedelta(hours=24)
VERIFICATION_TTL = timedelta(minutes=30)


@dataclass(slots=True)
class BeginEmailRegistrationHandler(
    CommandHandler[
        BeginEmailRegistration,
        EmailRegistrationStarted,
    ]
):
    registrations: RegistrationRepository
    workflows: RegistrationWorkflowRepository
    users: UserRepository
    challenges: EmailChallengeRepository

    lookup: RegistrationLookup
    access: RegistrationAccessService
    challenge_tokens: EmailChallengeTokenService

    outbox: OutboxWriter
    outbox_factory: OutboxMessageFactory

    db_session: AsyncSession
    clock: Clock

    async def __call__(
        self,
        command: BeginEmailRegistration,
    ) -> EmailRegistrationStarted:
        now = self.clock.now()
        email = EmailAddress(command.email)

        async with self.db_session.begin():
            context = await self.lookup.find_by_email(
                email,
                now=now,
            )

            if context.user_exists:
                raise  # TODO: email already register or not at all, prevent enumeration

            if context.has_active_registration:
                registration = context.registration
                workflow = context.workflow

                if registration is None or workflow is None:
                    raise RuntimeError("Registration lookup returned an incomplete context")

                resume_token = command.resume_token
                if resume_token is None:
                    raise RegistrationResumeTokenRequiredError()

                if not self.resume_tokens.verify(
                    ResumeToken(resume_token),
                    workflow.resume_token_hash,
                ):
                    raise RegistrationResumeTokenInvalidError()

                workflow.ensure_accessible(now=now)

                return EmailRegistrationStarted(
                    registration_id=registration.id,
                    method=registration.method,
                    step=workflow.step,
                    expires_at=workflow.expires_at,
                    resume_token=None,
                    resume_token_max_age=None,
                )

            resume_token, resume_token_hash = self.access.issue()
            registration = Registration.create(
                method=RegistrationMethod.EMAIL,
                expires_at=now + REGISTRATION_TTL,
                created_at=now,
            )

            registration.set_email(email, now=now)

            workflow = RegistrationWorkflow.start(
                registration=registration,
                resume_token_hash=resume_token_hash,
                expires_at=now + REGISTRATION_TTL,
                started_at=now,
                policy=self.policy,
            )

            challenge_token, challenge_token_hash = self.challenge_tokens.issue()
            challenge = EmailChallenge.create(
                registration_id=registration.id,
                email=email,
                token_hash=challenge_token_hash,
                purpose=EmailChallengePurpose.EMAIL_VERIFICATION,
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

        return EmailRegistrationStarted(
            registration_id=registration.id,
            method=registration.method,
            step=workflow.step,
            expires_at=registration.expires_at,
            resume_token=resume_token,
            resume_token_max_age=int(REGISTRATION_TTL.total_seconds()),
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

    # tokens: EmailChallengeTokenService
    registration_access: RegistrationAccessService

    db_session: AsyncSession
    clock: Clock

    async def __call__(
        self,
        command: VerifyRegistrationEmail,
    ) -> EmailVerificationResult:
        now = self.clock.now()
        challenge_token = EmailChallengeToken(command.challenge_token)

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

            token_hash = self.tokens.hash(challenge_token)
            challenge = await self.challenges.find_by_token_hash_for_update(
                token_hash,
            )
            if challenge is None:
                raise EmailChallengeInvalidTokenError()

            if challenge.registration_id != registration.id:
                raise EmailChallengeInvalidTokenError()

            challenge.complete(completed_at=now)
            registration.verify_email(now=now)

            # await self.challenges.update(challenge)
            # await self.registrations.update(registration)

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
    access: RegistrationAccessService

    password_policy: PasswordPolicy
    password_hasher: PasswordHasher

    registrations: RegistrationRepository
    db_session: AsyncSession
    clock: Clock

    async def __call__(
        self,
        command: SetRegistrationPassword,
    ) -> PasswordSet:
        now = self.clock.now()
        async with self.db_session.begin():
            registration = await self.access.require(
                command.resume_token,
            )

            self.password_policy.validate(command.password)
            password_hash = self.password_hasher.hash(command.password)
            registration.set_password(
                password_hash=password_hash,
                now=now,
            )

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
            active_challenge = await self.challenges.get_for_update(
                registration.id,
                now=now,
            )

            if active_challenge is not None:
                active_challenge.revoke(revoked_at=now)
                await self.challenges.update(active_challenge)

            challenge_token, challenge_token_hash = self.email_challenge.issue()

            challenge = EmailChallenge.create(
                registration_id=registration.id,
                email=email,
                token_hash=challenge_token_hash,
                purpose=EmailChallengePurpose.EMAIL_VERIFICATION,
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
