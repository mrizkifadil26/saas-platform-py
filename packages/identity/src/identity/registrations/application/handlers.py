from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from identity.accounts.application.ports import UserRepository
from identity.accounts.application.services import AccountService
from identity.registrations.domain import (
    EmailChallenge,
    EmailChallengePurpose,
    Registration,
    RegistrationMethod,
)
from identity.registrations.domain.enums import EmailChallengeMethod, RegistrationStep
from identity.registrations.domain.exceptions import (
    EmailChallengeError,
    InvalidEmailChallengeCodeError,
    InvalidEmailChallengeMethodError,
    InvalidEmailChallengeTokenError,
    RegistrationEmailAlreadyVerifiedError,
    RegistrationNotFoundError,
)
from identity.registrations.domain.policies import RegistrationPolicy
from identity.registrations.domain.value_objects import EmailChallengeCode, EmailChallengeToken
from identity.shared.application.command_bus import CommandHandler
from identity.shared.application.request_context import RequestContext
from identity.shared.domain.email import EmailAddress
from identity.shared.infrastructure.outbox import OutboxWriter
from identity.shared.infrastructure.outbox.message import OutboxMessageFactory
from identity.shared.infrastructure.security.password import PasswordHasher, PasswordPolicy
from identity.shared.infrastructure.time import Clock

from .commands import (
    BeginEmailRegistration,
    CompleteEmailRegistration,
    ResendEmailChallenge,
    SetRegistrationPassword,
    VerifyRegistrationEmailLink,
    VerifyRegistrationEmailOtp,
)
from .dto import (
    EmailChallengeResent,
    EmailRegistrationStarted,
    EmailVerificationResult,
    PasswordSet,
    RegistrationView,
)
from .ports import (
    EmailChallengeRepository,
    RegistrationLookup,
    RegistrationRepository,
)
from .services import (
    EmailChallengeCodeService,
    EmailChallengeThrottler,
    EmailChallengeTokenService,
    RegistrationAccessService,
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
    users: UserRepository
    challenges: EmailChallengeRepository

    lookup: RegistrationLookup
    access: RegistrationAccessService
    challenge_tokens: EmailChallengeTokenService
    challenge_codes: EmailChallengeCodeService

    outbox: OutboxWriter
    outbox_factory: OutboxMessageFactory

    db_session: AsyncSession
    clock: Clock

    challenge_method: EmailChallengeMethod

    async def __call__(
        self,
        command: BeginEmailRegistration,
        *,
        context: RequestContext,
    ) -> EmailRegistrationStarted:
        now = self.clock.now()
        email = EmailAddress(command.email)

        async with self.db_session.begin():
            lookup = await self.lookup.find_by_email(
                email,
                now=now,
            )

            if lookup.user_exists:
                raise  # TODO: email already register or not at all, prevent enumeration

            if lookup.has_active_registration:
                raise  # TODO: already started

            registration = Registration.create(
                method=RegistrationMethod.EMAIL,
                expires_at=now + REGISTRATION_TTL,
                created_at=now,
            )

            registration.set_email(
                email,
                now=now,
            )

            if self.challenge_method is EmailChallengeMethod.LINK:
                challenge_token, challenge_token_hash = self.challenge_tokens.issue()
                challenge = EmailChallenge.create(
                    registration_id=registration.id,
                    email=email,
                    method=EmailChallengeMethod.LINK,
                    token_hash=challenge_token_hash,
                    purpose=EmailChallengePurpose.EMAIL_VERIFICATION,
                    created_at=now,
                    expires_at=now + VERIFICATION_TTL,
                )

                message = self.outbox_factory.email_verification_link(
                    registration_id=registration.id,
                    challenge_id=challenge.id,
                    email=email,
                    token=challenge_token,
                )
            else:
                otp, code_hash = self.challenge_codes.issue()
                challenge = EmailChallenge.create(
                    registration_id=registration.id,
                    email=email,
                    method=EmailChallengeMethod.OTP,
                    code_hash=code_hash,
                    purpose=EmailChallengePurpose.EMAIL_VERIFICATION,
                    created_at=now,
                    expires_at=now + VERIFICATION_TTL,
                )

                message = self.outbox_factory.email_verification_otp(
                    registration_id=registration.id,
                    challenge_id=challenge.id,
                    email=email,
                    otp=otp,
                )

            await self.registrations.add(registration)
            await self.challenges.add(challenge)

            events = challenge.pull_events()
            await self.outbox.add_events(events)
            await self.outbox.add(message)
            # await self.outbox.add(
            #     OutboxMessage(
            #         id=uuid4(),
            #         message_type="email.verification.send",
            #         payload={
            #             "registration_id": str(registration.id),
            #             "challenge_id": str(challenge.id),
            #             "email": email.value,
            #             "token": challenge_token,
            #         },
            #         occurred_at=now,
            #     )
            # )

        return EmailRegistrationStarted(
            registration_id=registration.id,
            method=registration.method,
            step=RegistrationStep.EMAIL_CHALLENGE,
            expires_at=registration.expires_at,
        )


@dataclass(slots=True)
class VerifyRegistrationEmailLinkHandler(
    CommandHandler[
        VerifyRegistrationEmailLink,
        EmailVerificationResult,
    ]
):
    registrations: RegistrationRepository
    challenges: EmailChallengeRepository

    tokens: EmailChallengeTokenService
    registration_access: RegistrationAccessService

    db_session: AsyncSession
    clock: Clock

    async def __call__(
        self,
        command: VerifyRegistrationEmailLink,
        *,
        context: RequestContext,
    ) -> EmailVerificationResult:
        now = self.clock.now()

        challenge_token = EmailChallengeToken(command.challenge_token)
        challenge_token_hash = self.tokens.hash(challenge_token)

        async with self.db_session.begin():
            registration = await self.registrations.find_by_id_for_update(
                command.registration_id,
            )

            if registration is None:
                raise RegistrationNotFoundError()

            if registration.email_verified:
                return EmailVerificationResult(
                    registration=RegistrationView.from_result(registration),
                )

            challenge = await self.challenges.find_by_token_hash_for_update(challenge_token_hash)
            if challenge is None:
                raise InvalidEmailChallengeTokenError()

            if challenge.registration_id != registration.id:
                raise InvalidEmailChallengeTokenError()

            if challenge.method is not EmailChallengeMethod.LINK:
                raise InvalidEmailChallengeMethodError()

            challenge.complete(completed_at=now)
            registration.verify_email(now=now)

        return EmailVerificationResult(
            registration=RegistrationView.from_result(registration),
        )


@dataclass(slots=True)
class VerifyRegistrationEmailOtpHandler(
    CommandHandler[
        VerifyRegistrationEmailOtp,
        EmailVerificationResult,
    ]
):
    registrations: RegistrationRepository
    challenges: EmailChallengeRepository

    challenge_codes: EmailChallengeCodeService
    db_session: AsyncSession
    clock: Clock

    async def __call__(
        self,
        command: VerifyRegistrationEmailOtp,
        *,
        context: RequestContext,
    ) -> EmailVerificationResult:
        now = self.clock.now()

        otp = EmailChallengeCode(command.otp_code)

        async with self.db_session.begin():
            registration = await self.registrations.find_by_id_for_update(
                command.registration_id,
            )

            if registration is None:
                raise RegistrationNotFoundError()

            if registration.email_verified:
                return EmailVerificationResult(
                    registration=RegistrationView.from_result(registration),
                )

            challenge = await self.challenges.find_active_for_update(
                registration.id,
                purpose=EmailChallengePurpose.EMAIL_VERIFICATION,
                now=now,
            )

            if challenge is None:
                raise EmailChallengeError()

            if challenge.registration_id != registration.id:
                raise EmailChallengeError()

            if challenge.method is not EmailChallengeMethod.OTP:
                raise InvalidEmailChallengeMethodError()

            if challenge.code_hash is None:
                raise InvalidEmailChallengeCodeError()

            if not self.challenge_codes.verify(
                otp,
                challenge.code_hash,
            ):
                challenge.record_attempt()
                raise EmailChallengeError()

            challenge.complete(completed_at=now)
            registration.verify_email(now=now)

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
        *,
        context: RequestContext,
    ) -> PasswordSet:
        now = self.clock.now()
        async with self.db_session.begin():
            registration = await self.registrations.find_by_id_for_update(
                registration_id=command.registration_id,
            )
            if registration is None:
                raise RegistrationNotFoundError()

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
class ResendEmailChallengeHandler(
    CommandHandler[
        ResendEmailChallenge,
        EmailChallengeResent,
    ]
):
    registrations: RegistrationRepository
    challenges: EmailChallengeRepository

    tokens: EmailChallengeTokenService
    codes: EmailChallengeCodeService

    throttler: EmailChallengeThrottler

    outbox: OutboxWriter
    db_session: AsyncSession
    clock: Clock

    challenge_method: EmailChallengeMethod

    async def __call__(
        self,
        command: ResendEmailChallenge,
        *,
        context: RequestContext,
    ) -> EmailChallengeResent:
        now = self.clock.now()

        async with self.db_session.begin():
            registration = await self.registrations.find_by_id_for_update(
                command.registration_id,
            )

            if registration is None:
                raise RegistrationNotFoundError()

            # No point sending another verification email.
            registration.ensure_accessible(now=now)

            if registration.email_verified:
                raise RegistrationEmailAlreadyVerifiedError()

            # Prevent "send again" spam.
            email = registration.require_email()
            await self.throttler.enforce_resend(
                context=EmailChallengeThrottleContext(
                    email=email,
                    ip_address=context.client_ip or "",
                    registration_id=registration.id,
                )
            )

            # Invalidate the previous challenge.
            active_challenge = await self.challenges.find_active_for_update(
                registration.id,
                purpose=EmailChallengePurpose.EMAIL_VERIFICATION,
                now=now,
            )

            if active_challenge is not None:
                active_challenge.revoke(revoked_at=now)
                # await self.challenges.update(active_challenge)

            if self.challenge_method is EmailChallengeMethod.LINK:
                challenge_token, challenge_token_hash = self.tokens.issue()

                challenge = EmailChallenge.create(
                    registration_id=registration.id,
                    email=email,
                    method=EmailChallengeMethod.LINK,
                    token_hash=challenge_token_hash,
                    purpose=EmailChallengePurpose.EMAIL_VERIFICATION,
                    created_at=now,
                    expires_at=now + VERIFICATION_TTL,
                )

                message = self.outbox_factory.email_verification_link(
                    registration_id=registration.id,
                    challenge_id=challenge.id,
                    email=registration.email,
                    token=challenge_token,
                )

            else:
                challenge_code, challenge_code_hash = self.codes.issue()

                challenge = EmailChallenge.create(
                    registration_id=registration.id,
                    email=email,
                    method=EmailChallengeMethod.LINK,
                    code_hash=challenge_code_hash,
                    purpose=EmailChallengePurpose.EMAIL_VERIFICATION,
                    created_at=now,
                    expires_at=now + VERIFICATION_TTL,
                )

                message = self.outbox_factory.email_verification_otp(
                    registration_id=registration.id,
                    challenge_id=challenge.id,
                    email=registration.email,
                    otp=challenge_code,
                )

            await self.challenges.add(challenge)
            await self.outbox.add_events(challenge.pull_events())
            await self.outbox.add(message)

            # await self.outbox.add(
            #     OutboxMessage(
            #         id=uuid4(),
            #         message_type="email.verification.send",
            #         payload={
            #             "registration_id": str(registration.id),
            #             "challenge_id": str(challenge.id),
            #             "email": email.value,
            #             "token": challenge_token,
            #         },
            #         occurred_at=now,
            #     )
            # )

        return EmailChallengeResent(
            registration_id=registration.id,
            expires_at=challenge.expires_at,
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
    policy: RegistrationPolicy

    db_session: AsyncSession
    clock: Clock

    async def __call__(
        self,
        command: CompleteEmailRegistration,
        *,
        context: RequestContext,
    ) -> RegistrationView:
        now = self.clock.now()

        async with self.db_session.begin():
            registration = await self.registrations.find_by_id_for_update(
                command.registration_id,
            )

            if registration is None:
                raise RegistrationNotFoundError()

            if registration.is_completed:
                return RegistrationView.from_result(registration)

            user_id = await self.accounts.create_user(
                email=registration.require_email(),
                email_verified_at=registration.email_verified_at,
                created_at=now,
            )

            # user = await users.create_from_registration(registration)
            registration.complete(
                registration=registration,
                user_id=user_id,
                completed_at=now,
                policy=self.policy,
            )

            await self.registrations.update(registration)

        return RegistrationView.from_result(registration)
