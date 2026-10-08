from dataclasses import dataclass

from iam.authentication.application.commands import UUID


@dataclass(frozen=True, slots=True)
class IdentityContext:
    user_id: UUID
