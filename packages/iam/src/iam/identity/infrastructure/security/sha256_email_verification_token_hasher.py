import hashlib

from iam.identity.domain.value_objects import (
    EmailVerificationToken,
    EmailVerificationTokenHash,
)


class Sha256EmailVerificationTokenHasher:
    def hash(
        self,
        raw_token: EmailVerificationToken,
    ) -> EmailVerificationTokenHash:
        token_value = raw_token.value
        hashed_value = hashlib.sha256(
            token_value.encode("utf-8"),
        ).hexdigest()

        return EmailVerificationTokenHash(hashed_value)
