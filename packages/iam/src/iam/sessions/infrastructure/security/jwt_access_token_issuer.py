from datetime import datetime
from typing import Any

import jwt

from iam.sessions.application import AccessTokenPayload, AccessTokenProvider
from iam.sessions.domain import Session
from iam.sessions.domain.value_objects import AccessToken

from .jwt_config import JWTConfig


class JWTTokenProvider(AccessTokenProvider):
    def __init__(
        self,
        config: JWTConfig,
    ) -> None:
        self._config = config

    def issue(
        self,
        *,
        session: Session,
        expires_at: datetime,
        issued_at: datetime,
    ) -> tuple[
        AccessToken,
        AccessTokenPayload,
    ]:
        payload: dict[str, Any] = {
            "sub": str(session.user_id.value),
            "sid": str(session.id.value),
            "iss": self._config.issuer,
            "aud": self._config.audience,
            "iat": int(issued_at.timestamp()),
            "exp": int(expires_at.timestamp()),
        }

        encoded_token = jwt.encode(  # type: ignore
            payload,
            self._config.secret_key,
            algorithm=self._config.algorithm,
        )

        access_token = AccessToken(
            encoded_token,
        )

        token_payload = AccessTokenPayload(
            user_id=session.user_id,
            session_id=session.id,
            issued_at=issued_at,
            expires_at=expires_at,
        )

        return (
            access_token,
            token_payload,
        )
