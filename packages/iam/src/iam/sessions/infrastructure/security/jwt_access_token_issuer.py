from typing import Any
from uuid import uuid4

import jwt

from iam.authentication.infrastructure.config import JwtSettings
from iam.sessions.application.ports import AccessTokenClaims, AccessTokenIssuer
from iam.sessions.domain.value_objects import AccessToken


class JWTAccessTokenIssuer(AccessTokenIssuer):
    def __init__(
        self,
        config: JwtSettings,
    ) -> None:
        self._config = config

    def issue(
        self,
        claims: AccessTokenClaims,
    ) -> AccessToken:
        payload: dict[str, Any] = {
            "sub": claims.user_id,
            "sid": claims.session_id,
            "iat": claims.issued_at,
            "exp": claims.expires_at,
            "jti": str(uuid4()),
            "typ": "access",
        }

        encoded_token = jwt.encode(  # type: ignore
            payload,
            self._config.secret_key,
            algorithm=self._config.algorithm,
        )

        return AccessToken(encoded_token)
