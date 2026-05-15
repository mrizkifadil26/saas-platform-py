import hashlib

from iam.identity.domain import (
    EmailVerificationTokenHasher,
)
from iam.identity.domain.value_objects import (
    EmailVerificationToken,
    EmailVerificationTokenHash,
)


class Sha256EmailVerificationTokenHasher(EmailVerificationTokenHasher):
    def hash(self, raw_token: EmailVerificationToken) -> EmailVerificationTokenHash:
        str_token = str(raw_token)
        return EmailVerificationTokenHash(self._hash_token(str_token))

    def _hash_token(self, value: str) -> str:
        return hashlib.sha256(
            value.encode("utf-8"),
        ).hexdigest()
