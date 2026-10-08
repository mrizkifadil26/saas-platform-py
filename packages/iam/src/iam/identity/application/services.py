from dataclasses import dataclass

from iam.identity.application.ports import UserRepository


@dataclass(slots=True)
class IdentityReaderService:
    users: UserRepository

    