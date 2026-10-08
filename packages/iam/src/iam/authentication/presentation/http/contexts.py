from iam.identity.application.dto import UUID, dataclass


@dataclass(frozen=True, slots=True)
class AuthenticationContext:
    user_id: UUID
    session_id: UUID | None = None
