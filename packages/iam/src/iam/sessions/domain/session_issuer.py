from dataclasses import dataclass
from datetime import timedelta

from iam.identity.domain.value_objects import UserId
from iam.shared.domain.clock import Clock

from .interfaces import RefreshTokenGenerator, RefreshTokenHasher
from .refresh_token import RefreshToken
from .repositories import SessionRepository
from .session import Session


@dataclass(slots=True)
class SessionIssuer:
    session_repository: SessionRepository
    refresh_token_generator: RefreshTokenGenerator
    refresh_token_hasher: RefreshTokenHasher
    clock: Clock

    async def issue(
        self,
        *,
        user_id: UserId,
    ) -> Session:
        now = self.clock.now()

        raw_refresh_token = self.refresh_token_generator.generate()
        hashed_refresh_token = self.refresh_token_hasher.hash(raw_refresh_token)
        refresh_token = RefreshToken.create(
            token_hash=hashed_refresh_token,
            created_at=now,
            expires_at=now + timedelta(days=15),
        )

        session = Session.create(
            user_id=user_id,
            refresh_token=refresh_token,
            created_at=now,
        )

        await self.session_repository.save(session)

        return session
