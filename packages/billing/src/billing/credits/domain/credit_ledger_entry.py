from dataclasses import dataclass
from datetime import datetime

from billing.credits.domain.credit_source_type import CreditSourceType
from billing.credits.domain.exceptions import InvalidCreditAmountError
from billing.credits.domain.value_objects.credit_account_id import CreditAccountId
from billing.credits.domain.value_objects.credit_ledger_entry_id import (
    CreditLedgerEntryId,
)


@dataclass(frozen=True, slots=True)
class CreditLedgerEntry:
    id: CreditLedgerEntryId
    credit_account_id: CreditAccountId
    amount: int
    balance_after_available: int
    balance_after_reserved: int
    source_type: CreditSourceType
    source_id: str | None
    description: str | None
    occurred_at: datetime

    def __post_init__(self) -> None:
        if self.amount == 0:
            raise InvalidCreditAmountError("Credit ledger entry amount cannot be zero")

        if self.balance_after_available < 0:
            raise InvalidCreditAmountError("Balance after available cannot be negative")

        if self.balance_after_reserved < 0:
            raise InvalidCreditAmountError("Balance after reserved cannot be negative")
