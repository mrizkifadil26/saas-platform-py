from identity.shared.infrastructure.security.passwords.config import PasswordConfig
from identity.shared.infrastructure.security.passwords.contracts import PasswordService


class Argon2PasswordService(PasswordService):
    def __init__(self, config: PasswordConfig):
        self._config = config

    def hash(self, password: str) -> str:
        raise NotImplementedError

    def verify(self, password: str, password_hash: str) -> bool:
        raise NotImplementedError
