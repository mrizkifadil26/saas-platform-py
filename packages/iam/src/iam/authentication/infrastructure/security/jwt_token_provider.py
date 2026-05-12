from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt

from iam.authentication.application import AuthTokens
from iam.identity.domain.value_objects import UserId


class JWTTokenProvider:
    ALGORITHM = "HS256"

    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_token_minutes: int,
        refresh_token_days: int,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_minutes = access_token_minutes
        self._refresh_token_days = refresh_token_days

    async def generate_access_token(
        self,
        user_id: UserId,
        # TODO: org_id,
        # TODO: permissions,
        *,
        issued_at: datetime,
    ) -> AuthTokens:
        return AuthTokens(
            access_token=self._create_access_token(
                user_id,
                issued_at=issued_at,
            ),
            refresh_token=self._create_refresh_token(
                user_id,
                issued_at=issued_at,
            ),
        )

    def _create_access_token(
        self,
        user_id: UserId,
        # TODO: orgz_id
        # TODO: permissions,
        *,
        issued_at: datetime,
    ) -> str:
        payload: dict[str, Any] = {
            "jti": str(uuid4()),
            "sub": str(user_id.value),
            "type": "access",
            "iat": issued_at,
            "exp": issued_at
            + timedelta(
                days=self._access_token_minutes,
            ),
            # "permissions": sorted(permissions),
        }

        # if org_id is not None:
        #     payload["org_id"] = str(org_id.value)

        return jwt.encode(  # type: ignore
            payload,
            self._secret_key,
            algorithm=self._algorithm,
        )

    def _create_refresh_token(
        self,
        user_id: UserId,
        *,
        issued_at: datetime,
    ) -> str:
        payload: dict[str, Any] = {
            "jti": str(uuid4()),
            "sub": str(user_id.value),
            "type": "refresh",
            "iat": issued_at,
            "exp": issued_at
            + timedelta(
                days=self._refresh_token_days,
            ),
        }

        return jwt.encode(  # type: ignore
            payload,
            self._secret_key,
            algorithm=self._algorithm,
        )
