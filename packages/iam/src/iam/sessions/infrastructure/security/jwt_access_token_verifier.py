import jwt

from iam.authentication.infrastructure.config import JwtSettings
from iam.sessions.application.ports import AccessTokenClaims, AccessTokenVerifier
from iam.sessions.domain.value_objects import AccessToken


class JWTAccessTokenVerifier(AccessTokenVerifier):
    def __init__(
        self,
        config: JwtSettings,
    ) -> None:
        self._config = config

    def verify(
        self,
        token: AccessToken,
    ) -> AccessTokenClaims | None:
        try:
            payload = jwt.decode(  # type: ignore
                token.value,
                self._config.secret_key,
                algorithm=[self._config.algorithm],
            )
        except jwt.InvalidTokenError:
            return None

        if payload.get("typ") != "access":
            return None

        return AccessTokenClaims(
            user_id=payload["sub"],
            session_id=payload["sid"],
            issued_at=payload["iat"],
            expires_at=payload["exp"],
        )
