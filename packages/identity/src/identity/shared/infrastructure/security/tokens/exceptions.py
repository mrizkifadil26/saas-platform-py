class TokenError(Exception):
    """Base class for token-related errors."""


class InvalidToken(TokenError):
    """Token is malformed, invalid, or otherwise unacceptable."""


class ExpiredToken(TokenError):
    """Token has expired."""


class InvalidTokenClaims(TokenError):
    """Token contains invalid application claims."""
