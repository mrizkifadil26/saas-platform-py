import uuid
from datetime import UTC, datetime, timedelta

import jwt

from auth.errors import InvalidAccessToken
from auth.settings import AuthSettings
from auth.types import AccessTokenClaims, AuthenticatedSubject


def _utcnow() -> datetime:
    return datetime.now(UTC)


def mint_access_token(
    *,
    settings: AuthSettings,
    user_id: uuid.UUID,
    workspace_id: uuid.UUID,
    session_id: uuid.UUID,
) -> tuple[str, datetime]:
    now = _utcnow()
    exp = now + timedelta(minutes=settings.ACCESS_TOKEN_TTL_MINUTES)

    claims: AccessTokenClaims = {
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "sub": str(user_id),
        "sid": str(session_id),
        "wid": str(workspace_id),
        "typ": "access",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": str(uuid.uuid4()),
    }

    token = jwt.encode(
        claims,  # type: ignore[arg-type]
        key=settings.JWT_SECRET,
        algorithm=settings.JWT_ALG,
    )

    return token, exp


def verify_access_token(
    *,
    settings: AuthSettings,
    token: str,
) -> AccessTokenClaims:
    try:
        claims = jwt.decode(
            token,
            key=settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
            options={"require": ["exp", "iat", "iss", "aud", "sub", "jti"]},
        )
    except jwt.ExpiredSignatureError as e:
        raise InvalidAccessToken("token expired") from e
    except jwt.PyJWKError as e:
        raise InvalidAccessToken("token invalid") from e

    if claims.get("typ") != "access":
        raise InvalidAccessToken("wrong token type")

    # TypeDict cast-ish: we validate required keys above
    return claims  # type: ignore[return-value]


def subject_from_access_token(
    *,
    settings: AuthSettings,
    token: str,
) -> AuthenticatedSubject:
    """Verify access token and return the authenticated subject (for middleware)."""
    claims = verify_access_token(settings=settings, token=token)
    return AuthenticatedSubject(
        user_id=uuid.UUID(claims["sub"]),
        workspace_id=uuid.UUID(claims["wid"]),
        session_id=uuid.UUID(claims["sid"]),
    )
