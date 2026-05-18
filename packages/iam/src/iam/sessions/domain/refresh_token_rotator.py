from dataclasses import dataclass
from datetime import timedelta

from iam.shared.domain.clock import Clock

from .interfaces import RefreshTokenGenerator, RefreshTokenHasher
from .refresh_token import RefreshToken
from .repositories import RefreshTokenRepository, SessionRepository


@dataclass(slots=True)
class RefreshTokenRotator:
    session_repository: SessionRepository
    refresh_token_repository: RefreshTokenRepository

    refresh_token_generator: RefreshTokenGenerator
    refresh_token_hasher: RefreshTokenHasher
    clock: Clock

    async def rotate(
        self,
        *,
        raw_refresh_token: str,
    ) -> str:
        now = self.clock.now()

        token_hash = self.refresh_token_hasher.hash(
            raw_refresh_token,
        )

        current_token = await self.refresh_token_repository.find_by_token_hash(
            token_hash,
        )

        if current_token is None:
            # TODO: raise invalid refresh token
            raise

        session = await self.session_repository.find_by_id(
            current_token.session_id,
        )
        if session is None:
            # TODO: raise session not found error
            raise

        if session.is_revoked:
            # TODO: raise session revoked error
            raise

        if session.is_expired(now=now):
            # TODO: raise session expired error
            raise

        if current_token.is_revoked:
            session.revoke(revoked_at=now)
            await self.session_repository.save(session)

            # TODO: raise refresh token reuse
            raise

        new_raw_token = self.refresh_token_generator.generate()
        new_token_hash = self.refresh_token_hasher.hash(new_raw_token)

        new_refresh_token = RefreshToken.create(
            session_id=session.id,
            token_hash=new_token_hash,
            created_at=now,
            expires_at=now + timedelta(days=15),
            parent_token_id=current_token.id,
        )

        current_token.revoke(
            revoked_at=now,
            replaced_by=new_refresh_token.id,
        )

        current_token.mark_used(
            used_at=now,
        )

        await self.refresh_token_repository.update(current_token)
        await self.refresh_token_repository.save(new_refresh_token)

        await self.session_repository.save(session)

        return new_raw_token
