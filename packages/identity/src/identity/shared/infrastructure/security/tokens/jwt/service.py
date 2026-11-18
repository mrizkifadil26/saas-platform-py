from identity.shared.infrastructure.security.tokens.config import TokenConfig
from identity.shared.infrastructure.security.tokens.contracts import TokenService


class JwtTokenService(TokenService):
    def __init__(self, config: TokenConfig):
        self._config = config
