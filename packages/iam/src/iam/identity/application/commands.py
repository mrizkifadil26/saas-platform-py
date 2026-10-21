from dataclasses import dataclass, field

from iam.identity.domain.enums import IdentityProvider
from iam.identity.domain.value_objects import ExternalIdentityId
from iam.shared.application.command_bus import Command


@dataclass(frozen=True, slots=True)
class AuthenticateExternal(Command):
    provider: IdentityProvider
    authorization_code: str = field(repr=False)
    state: str = field(repr=False)
    # redirect_uri: str


@dataclass(frozen=True, slots=True)
class LinkExternalIdentity(Command):
    provider: IdentityProvider
    authorization_code: str = field(repr=False)
    state: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class UnlinkExternalIdentity(Command):
    external_identity_id: ExternalIdentityId
