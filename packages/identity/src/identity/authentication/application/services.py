from datetime import datetime

from tests.factories.identity import timedelta

from identity.accounts.domain.value_objects import UserId
from identity.sessions.domain.value_objects import SessionId
from identity.shared.infrastructure.security.tokens import AccessTokenClaims, JWTEncoder


class AccessTokenService:
    def __init__(
        self,
        *,
        encoder: JWTEncoder,
        issuer: str,
        audience: str,
        lifetime: timedelta,
    ) -> None:
        self._encoder = encoder
        self._issuer = issuer
        self._audience = audience
        self._lifetime = lifetime

    def issue(
        self,
        *,
        user_id: UserId,
        session_id: SessionId,
        issued_at: datetime,
        scopes: tuple[str, ...] = (),
    ) -> str:
        expires_at = issued_at + self._lifetime

        claims = AccessTokenClaims(
            subject=str(user_id),
            session_id=str(session_id),
            issued_at=issued_at,
            expires_at=expires_at,
            issuer=self._issuer,
            audience=self._audience,
            scopes=scopes,
        )

        return self._encoder.encode(claims)
