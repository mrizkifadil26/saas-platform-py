from __future__ import annotations

import secrets


class SecureTokenGenerator:
    """
    Generates cryptographically secure opaque tokens.

    Used for:
    - refresh tokens
    - registration resume tokens
    - email challenge tokens
    """

    def __init__(
        self,
        *,
        default_bytes: int = 32,
    ) -> None:
        if default_bytes < 16:
            raise ValueError("Token size must be at least 16 bytes")

        self._default_bytes = default_bytes

    def generate(
        self,
        *,
        bytes_length: int | None = None,
    ) -> str:
        size = bytes_length or self._default_bytes

        if size < 16:
            raise ValueError("Token size must be at least 16 bytes")

        return secrets.token_urlsafe(size)


