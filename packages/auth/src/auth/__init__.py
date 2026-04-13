"""Auth package: JWT access tokens, opaque refresh tokens, Argon2 passwords.

Public API:
- Flows: login, refresh, logout, register
- Middleware: subject_from_access_token
- Config: AuthSettings
- Types: TokenPair, AuthenticatedSubject, AccessTokenClaims
- Exceptions: AuthError, InvalidAccessToken, InvalidCredentials, etc.
- Ports: auth.ports (AuthUoWPort, repo protocols)
- Crypto: auth.crypto (hash_password, verify_password, mint_refresh_token, hash_refresh_token)
"""

from auth import crypto, errors, ports, service, settings, tokens, types
from auth.errors import (
    AuthError,
    EmailAlreadyRegistered,
    InvalidAccessToken,
    InvalidCredentials,
    SessionExpired,
    SessionNotFound,
    SessionRevoked,
    UserInactive,
)
from auth.service import login, logout, refresh, register
from auth.settings import AuthSettings
from auth.tokens import (
    mint_access_token,
    subject_from_access_token,
    verify_access_token,
)
from auth.types import AccessTokenClaims, AuthenticatedSubject, TokenPair

__all__ = [
    "AccessTokenClaims",
    "AuthError",
    "AuthSettings",
    "AuthenticatedSubject",
    "EmailAlreadyRegistered",
    "InvalidAccessToken",
    "InvalidCredentials",
    "SessionExpired",
    "SessionNotFound",
    "SessionRevoked",
    "TokenPair",
    "UserInactive",
    "crypto",
    "errors",
    "login",
    "logout",
    "mint_access_token",
    "ports",
    "refresh",
    "register",
    "service",
    "settings",
    "subject_from_access_token",
    "tokens",
    "types",
    "verify_access_token",
]
