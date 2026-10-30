from __future__ import annotations

import jwt
from jwt import InvalidTokenError as PyJWTInvalidTokenError

from .exceptions import ExpiredToken, InvalidToken
from .types import AccessTokenClaims


class JWTEncoder:
    def __init__(
        self,
        *,
        secret: str,
        algorithm: str = "HS256",
    ) -> None:
        self._secret = secret
        self._algorithm = algorithm

    def encode(
        self,
        claims: AccessTokenClaims,
    ) -> str:
        payload = claims.to_payload()

        return jwt.encode(  # type: ignore
            payload,
            self._secret,
            algorithm=self._algorithm,
        )


class JWTDecoder:
    def __init__(
        self,
        *,
        secret: str,
        issuer: str,
        audience: str,
        algorithm: str = "HS256",
    ) -> None:
        self._secret = secret
        self._issuer = issuer
        self._audience = audience
        self._algorithm = algorithm

    def decode(
        self,
        token: str,
    ) -> AccessTokenClaims:
        try:
            payload = jwt.decode(  # type: ignore
                token,
                self._secret,
                algorithms=[self._algorithm],
                issuer=self._issuer,
                audience=self._audience,
                options={
                    "require": [
                        "sub",
                        "sid",
                        "iat",
                        "exp",
                        "iss",
                        "aud",
                    ],
                },
            )
        except jwt.ExpiredSignatureError as exc:
            raise ExpiredToken("Access token has expired") from exc
        except PyJWTInvalidTokenError as exc:
            raise InvalidToken("Invalid access token") from exc

        try:
            return AccessTokenClaims.from_payload(payload)
        except ValueError as exc:
            raise InvalidToken("Invalid access token claims") from exc
