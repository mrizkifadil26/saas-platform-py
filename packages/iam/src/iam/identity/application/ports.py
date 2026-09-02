from typing import Protocol

from iam.identity.domain.value_objects import (
    EmailVerificationToken,
    EmailVerificationTokenHash,
)


class EmailVerificationTokenGenerator(Protocol):
    def generate(self) -> EmailVerificationToken: ...


class EmailVerificationTokenHasher(Protocol):
    def hash(
        self,
        raw_token: EmailVerificationToken,
    ) -> EmailVerificationTokenHash: ...
