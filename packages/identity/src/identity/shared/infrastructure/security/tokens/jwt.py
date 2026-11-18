from __future__ import annotations

from identity.shared.infrastructure.security.tokens.config import TokenConfig


class JwtTokenService:
    def __init__(self, config: TokenConfig):
        self._config = config


