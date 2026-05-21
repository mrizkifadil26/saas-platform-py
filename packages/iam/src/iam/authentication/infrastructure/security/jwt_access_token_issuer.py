from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt

from iam.authentication.application import AccessTokenIssuer
from iam.authentication.domain.value_objects import AccessToken
from iam.authentication.infrastructure.config import JwtSettings


class JWTAccessTokenIssuer(AccessTokenIssuer):
    def __init__(
        self,
        config: JwtSettings,
    ) -> None:
        self._config = config

    def issue(
        self,
        claims: dict[str, Any],
        expires_in: timedelta | None = None,
    ) -> AccessToken:
        now = datetime.now(UTC)
        ttl = expires_in or timedelta(minutes=15)

        expires_at = now + ttl

        payload: dict[str, Any] = {
            "sub": claims["sub"],
            "roles": claims["roles"],
            "iat": now,
            "exp": expires_at,
            "jti": str(uuid4()),
            "typ": "access",
        }

        encoded_token = jwt.encode(  # type: ignore
            payload,
            self._config.secret_key,
            algorithm=self._config.algorithm,
        )

        return AccessToken(encoded_token)
