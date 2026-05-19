from dataclasses import dataclass
from datetime import timedelta

from iam.identity.domain.value_objects import UserId
from iam.shared.domain.clock import Clock

from .interfaces import RefreshTokenGenerator, RefreshTokenHasher
from .refresh_token import RefreshToken
from .session import Session


@dataclass(frozen=True, slots=True)
class IssuedSession:
    session: Session
    refresh_token: str


@dataclass(slots=True)
class SessionIssuer:
    refresh_token_generator: RefreshTokenGenerator
    refresh_token_hasher: RefreshTokenHasher

    clock: Clock

    refresh_token_ttl: timedelta

    async def issue(
        self,
        *,
        user_id: UserId,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> IssuedSession:
        now = self.clock.now()

        session = Session.create(
            user_id=user_id,
            created_at=now,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        raw_refresh_token = self.refresh_token_generator.generate()
        token_hash = self.refresh_token_hasher.hash(raw_refresh_token)

        refresh_token = RefreshToken.create(
            session_id=session.id,
            token_hash=token_hash,
            created_at=now,
            expires_at=now + self.refresh_token_ttl,
        )

        session.attach_refresh_token(
            refresh_token_id=refresh_token.id,
            now=now,
        )

        return IssuedSession(
            session=session,
            refresh_token=raw_refresh_token,
        )
