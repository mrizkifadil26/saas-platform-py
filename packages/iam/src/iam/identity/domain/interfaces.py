from datetime import datetime
from typing import Protocol

from .value_objects import (
    EmailVerificationToken,
    EmailVerificationTokenHash,
)


class EmailVerificationTokenGenerator(Protocol):
    def generate(self) -> EmailVerificationToken: ...


class EmailVerificationTokenHasher(Protocol):
    def hash(self, raw_token: EmailVerificationToken) -> EmailVerificationTokenHash: ...


class Clock(Protocol):
    def now(self) -> datetime: ...
