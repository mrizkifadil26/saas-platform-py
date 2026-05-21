import hashlib

from iam.identity.application import (
    EmailVerificationTokenHasher,
)
from iam.identity.domain.value_objects import (
    EmailVerificationToken,
    EmailVerificationTokenHash,
)


class Sha256EmailVerificationTokenHasher(
    EmailVerificationTokenHasher,
):
    def hash(
        self,
        raw_token: EmailVerificationToken,
    ) -> EmailVerificationTokenHash:
        token_value = raw_token.unwrap()

        return EmailVerificationTokenHash(
            self._compute_hash(token_value),
        )

    def verify(
        self,
        raw_token: EmailVerificationToken,
        hashed_token: EmailVerificationTokenHash,
    ) -> bool:
        return self.hash(raw_token) == hashed_token

    def _compute_hash(
        self,
        value: str,
    ) -> str:
        return hashlib.sha256(
            value.encode("utf-8"),
        ).hexdigest()
