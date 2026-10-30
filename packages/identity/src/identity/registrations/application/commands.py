from dataclasses import dataclass, field

from identity.registrations.domain.value_objects import RegistrationId, ResumeToken
from identity.shared.application.command_bus.bus import Command


@dataclass(frozen=True, slots=True)
class BeginEmailRegistration(Command):
    email: str
    resume_token: str | None = None


@dataclass(frozen=True, slots=True)
class BeginGoogleRegistration(Command):
    authorization_code: str


# @dataclass(frozen=True, slots=True)
# class BeginOIDCRegistration(Command):
#     identity: VerifiedOIDCIdentity


@dataclass(frozen=True, slots=True)
class VerifyRegistrationEmail(Command):
    registration_id: RegistrationId
    challenge_token: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class SetRegistrationPassword(Command):
    registration_id: RegistrationId
    resume_token: ResumeToken
    password: str


@dataclass(frozen=True, slots=True)
class CompleteGoogleRegistration(Command):
    registration_id: RegistrationId


@dataclass(frozen=True, slots=True)
class CompleteEmailRegistration(Command):
    registration_id: RegistrationId


@dataclass(frozen=True, slots=True)
class ResendEmailVerification(Command):
    registration_id: RegistrationId
    resume_token: ResumeToken | None
    # challenge_token: str = field(repr=False)

    ip_address: str


@dataclass(frozen=True, slots=True)
class CancelRegistration(Command):
    registration_id: RegistrationId
    resume_token: str = field(repr=False)
