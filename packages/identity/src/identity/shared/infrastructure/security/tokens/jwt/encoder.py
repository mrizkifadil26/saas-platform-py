class JwtEncoder:
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

