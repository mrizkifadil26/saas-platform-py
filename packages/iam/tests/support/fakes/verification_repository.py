# tests/support/fakes/user_repository.py

from dataclasses import dataclass, field

from iam.identity.domain import EmailVerificationRepository
from iam.identity.domain.email_verification import EmailVerification
from iam.identity.domain.value_objects import (
    EmailVerificationId,
    EmailVerificationTokenHash,
    UserId,
)


@dataclass(slots=True)
class InMemoryEmailVerificationRepository(EmailVerificationRepository):
    email_verifications: dict[object, EmailVerification] = field(
        default_factory=lambda: dict[object, EmailVerification](),
    )

    async def save(
        self,
        verification: EmailVerification,
    ) -> None:
        self.email_verifications[verification.id] = verification

    async def find_by_id(
        self,
        verification_id: EmailVerificationId,
    ) -> EmailVerification | None:
        return self.email_verifications.get(verification_id)

    async def find_by_user_id(
        self,
        user_id: UserId,
    ) -> EmailVerification | None:
        return next(
            (
                verification
                for verification in self.email_verifications.values()
                if verification.user_id == user_id
            ),
            None,
        )

    async def find_by_token_hash(
        self,
        token_hash: EmailVerificationTokenHash,
    ) -> EmailVerification | None:
        return next(
            (
                verification
                for verification in self.email_verifications.values()
                if verification.token_hash == token_hash
            ),
            None,
        )
