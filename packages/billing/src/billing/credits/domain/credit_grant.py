from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime

from billing.credits.domain.exceptions import (
    CreditGrantOverConsumedError,
    InvalidCreditsAmountError,
)
from billing.credits.domain.value_objects.credit_account_id import CreditAccountId
from billing.credits.domain.value_objects.credit_grant_id import CreditGrantId
from billing.credits.domain.value_objects.credits import Credits


@dataclass(frozen=True, slots=True)
class CreditGrant:
    id: CreditGrantId
    credit_account_id: CreditAccountId
    amount: Credits
    remaining: Credits
    granted_at: datetime
    expires_at: datetime | None = None
    source_id: str | None = None

    def __post_init__(self) -> None:
        if self.amount.is_zero():
            raise InvalidCreditsAmountError(
                "Credit grant amount must be greater than zero."
            )

        if self.remaining > self.amount:
            raise InvalidCreditsAmountError(
                "Credit grant remaining amount cannot be greater than the granted amount"
            )

        if self.expires_at is not None and self.expires_at <= self.granted_at:
            raise InvalidCreditsAmountError(
                "Credit grant expiration date must be after the granted date"
            )

    def is_expired_at(self, at: datetime) -> bool:
        return self.expires_at is not None and at >= self.expires_at

    def is_fully_consumed(self) -> bool:
        return self.remaining.is_zero()

    def consume(self, amount: Credits) -> CreditGrant:
        if amount.is_zero():
            raise InvalidCreditsAmountError(
                "Amount to consume must be greater than zero."
            )

        if amount > self.remaining:
            raise CreditGrantOverConsumedError(
                requested=int(amount),
                remaining=int(self.remaining),
            )

        return replace(
            self,
            remaining=self.remaining - amount,
        )

    def expire(self, at: datetime) -> CreditGrant:
        if not self.is_expired_at(at) or self.remaining.is_zero():
            return self

        return replace(
            self,
            remaining=Credits.zero(),
        )
