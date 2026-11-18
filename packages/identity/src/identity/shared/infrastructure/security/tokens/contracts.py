from typing import Protocol


class TokenService(Protocol):
    def issue(self): ...

    def verify(self): ...