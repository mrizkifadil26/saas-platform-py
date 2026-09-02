from dataclasses import dataclass
from datetime import datetime, timedelta

from iam.identity.domain.value_objects import UserId
from iam.sessions.application.dto import IssuedSession
from iam.sessions.domain import RefreshToken, Session
from iam.sessions.domain.value_objects import RefreshTokenSecret

from .api import SessionIssuer
from .dto import RotatedSessionTokens
from .ports import (
    AccessTokenClaims,
    AccessTokenIssuer,
    RefreshTokenGenerator,
    RefreshTokenHasher,
    SessionUnitOfWork,
)


@dataclass(slots=True)
class IssueSessionService(SessionIssuer):
    unit_of_work: SessionUnitOfWork

    refresh_token_generator: RefreshTokenGenerator
    refresh_token_hasher: RefreshTokenHasher
    access_token_issuer: AccessTokenIssuer

    session_ttl: timedelta
    refresh_token_ttl: timedelta
    access_token_ttl: timedelta

    async def issue(
        self,
        *,
        user_id: UserId,
        issued_at: datetime,
    ) -> IssuedSession:
        session = Session.create(
            user_id=user_id,
            created_at=issued_at,
            expires_at=issued_at + self.session_ttl,
        )

        raw_refresh_token = self.refresh_token_generator.generate()
        refresh_token_hash = self.refresh_token_hasher.hash(
            raw_refresh_token,
        )

        refresh_token = RefreshToken.create(
            session_id=session.id,
            token_hash=refresh_token_hash,
            created_at=issued_at,
            expires_at=issued_at + self.refresh_token_ttl,
        )

        session.attach_refresh_token(
            refresh_token.id,
            now=issued_at,
        )

        async with self.unit_of_work as uow:
            await uow.sessions.save(session)
            await uow.refresh_tokens.save(refresh_token)

            await uow.commit()

        access_token = self.access_token_issuer.issue(
            AccessTokenClaims(
                user_id=user_id,
                session_id=session.id,
                issued_at=issued_at,
                expires_at=issued_at + self.access_token_ttl,
            )
        )

        return IssuedSession(
            session_id=session.id,
            access_token=access_token,
            refresh_token=raw_refresh_token,
        )


@dataclass(slots=True)
class RotateRefreshTokenService:
    unit_of_work: SessionUnitOfWork

    token_generator: RefreshTokenGenerator
    token_hasher: RefreshTokenHasher
    access_token_issuer: AccessTokenIssuer

    refresh_token_ttl: timedelta
    access_token_ttl: timedelta

    async def rotate(
        self,
        *,
        raw_token: RefreshTokenSecret,
        now: datetime,
    ) -> RotatedSessionTokens:
        token_hash = self.token_hasher.hash(raw_token)

        async with self.unit_of_work as uow:
            current_token = await uow.refresh_tokens.find_by_token_hash(
                token_hash,
            )

            if current_token is None:
                # raise InvalidRefreshTokenError()
                raise

            session = await uow.sessions.find_by_id(
                current_token.session_id,
            )

            if session is None:
                # raise InvalidRefreshTokenError()
                raise

            if not session.is_active(now=now):
                # raise SessionInactiveError()
                raise

            if not current_token.is_active(now=now):
                # raise InvalidRefreshTokenError()
                raise

            if session.current_refresh_token_id != current_token.id:
                # raise RefreshTokenReuseDetectedError()
                raise

            # if current_token.session_id != session.id:
                # raise InvalidRefreshTokenError()
                # raise

            new_raw_token = self.token_generator.generate()
            new_token_hash = self.token_hasher.hash(new_raw_token)

            new_token = RefreshToken.create(
                session_id=session.id,
                token_hash=new_token_hash,
                created_at=now,
                expires_at=now + self.refresh_token_ttl,
                parent_token_id=current_token.id,
            )

            current_token.replace_with(
                new_token.id,
                used_at=now,
            )

            session.rotate_to(
                current_token_id=current_token.id,
                new_token_id=new_token.id,
                now=now,
            )

            new_access_token = self.access_token_issuer.issue(
                AccessTokenClaims(
                    user_id=session.user_id,
                    session_id=session.id,
                    issued_at=now,
                    expires_at=now + self.access_token_ttl,
                ),
            )

            await uow.refresh_tokens.save(current_token)
            await uow.refresh_tokens.save(new_token)
            await uow.sessions.save(session)

            await uow.commit()

        return RotatedSessionTokens(
            refresh_token=new_raw_token,
            access_token=new_access_token,
        )
