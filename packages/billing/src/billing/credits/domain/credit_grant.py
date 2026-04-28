from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from billing.credits.domain.exceptions import (
    CreditGrantOverConsumedError,
    InvalidCreditAmountError,
)
from billing.credits.domain.value_objects.credit_account_id import CreditAccountId
from billing.credits.domain.value_objects.credit_grant_id import CreditGrantId


@dataclass(frozen=True, slots=True)
class CreditGrant:
    id: CreditGrantId
    credit_account_id: CreditAccountId
    amount: int
    remaining: int
    granted_at: datetime
    expires_at: datetime | None = None
    source_id: str | None = None

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise InvalidCreditAmountError("Credit grant amount cannot be negative")

        if self.remaining < 0:
            raise InvalidCreditAmountError(
                "Credit grant remaining amount cannot be negative"
            )

        if self.remaining > self.amount:
            raise InvalidCreditAmountError(
                "Credit grant remaining amount cannot be greater than the granted amount"
            )

        if self.expires_at is not None and self.expires_at <= self.granted_at:
            raise InvalidCreditAmountError(
                "Credit grant expiration date must be after the granted date"
            )

    def is_expired_at(self, at: datetime) -> bool:
        if self.expires_at is None:
            return False

        return at >= self.expires_at

    def consume(self, amount: int) -> CreditGrant:
        if amount <= 0:
            raise ValueError("Amount to consume cannot be zero or negative")

        if amount > self.remaining:
            raise CreditGrantOverConsumedError(
                requested=amount,
                remaining=self.remaining,
            )

        return CreditGrant(
            id=self.id,
            credit_account_id=self.credit_account_id,
            amount=self.amount,
            remaining=self.remaining - amount,
            granted_at=self.granted_at,
            expires_at=self.expires_at,
            source_id=self.source_id,
        )

    def expire(self, at: datetime) -> CreditGrant:
        if self.is_expired_at(at):
            return CreditGrant(
                id=self.id,
                credit_account_id=self.credit_account_id,
                amount=self.amount,
                remaining=0,
                granted_at=self.granted_at,
                expires_at=self.expires_at,
                source_id=self.source_id,
            )

        return self
