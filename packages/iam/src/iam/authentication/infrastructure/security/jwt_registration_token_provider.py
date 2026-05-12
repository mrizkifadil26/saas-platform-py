from datetime import datetime

import jwt

from iam.authentication.application.interfaces import RegistrationTokenProvider
from iam.authentication.domain.value_objects import RegistrationToken
from iam.identity.domain.value_objects import UserId

from .jwt_config import JWTConfig
from .jwt_payloads import (
    RegistrationTokenPayload,
)


class JWTRegistrationTokenProvider(
    RegistrationTokenProvider,
):
    ALGORITHM = "HS256"

    def __init__(
        self,
        # secret_key: str,
        # algorithm: str,
        # expires_minutes: int,
        config: JWTConfig,
    ) -> None:
        # self._secret_key = secret_key
        # self._algorithm = algorithm
        # self._expires_minutes = expires_minutes
        self._config = config

    async def generate_token(
        self,
        user_id: UserId,
        *,
        issued_at: datetime,
    ) -> RegistrationToken:
        payload: dict[str, object] = {
            "sub": user_id.value,
            "iss": self._config.issuer,
            "type": "registration",
            # "email": email.value,
            "iat": issued_at,
            "exp": int(
                (issued_at + self._config.registration_expiration).timestamp(),
            ),
        }

        return jwt.encode(  # type: ignore
            payload,
            self._config.registration_secret_key,
            algorithm=self.ALGORITHM,
        )

    async def verify_token(
        self,
        token: RegistrationToken,
    ) -> RegistrationTokenPayload:
        try:
            payload = jwt.decode(  # type: ignore
                token.value,
                self._config.registration_secret_key,
                algorithms=[self.ALGORITHM],
                options={"require": ["type", "sub", "iat", "exp"]},
            )

            if payload["type"] != "registration":
                # TODO: raise invalid token exception
                # raise InvalidTokenError()
                raise

            return RegistrationTokenPayload(
                user_id=UserId(payload["sub"]),
            )
        except jwt.ExpiredSignatureError as error:
            # TODO: raise typed exception
            # raise ValueError("Token has expired") from error
            raise error
        except jwt.InvalidTokenError as error:
            # TODO: raise typed exception
            # raise ValueError("Invalid token") from error
            raise error
