from dataclasses import dataclass
from datetime import datetime

from billing.credits.domain.credit_source_type import CreditSourceType
from billing.credits.domain.exceptions import (
    InvalidCreditLedgerEntryError,
)
from billing.credits.domain.value_objects.credit_account_id import CreditAccountId
from billing.credits.domain.value_objects.credit_ledger_entry_id import (
    CreditLedgerEntryId,
)
from billing.credits.domain.value_objects.credits import Credits


@dataclass(frozen=True, slots=True)
class CreditLedgerEntry:
    id: CreditLedgerEntryId
    credit_account_id: CreditAccountId

    # Signed delta:
    # + credits granted/released
    # - credits reserved/consumed/expired
    delta: int

    balance_after_available: Credits
    balance_after_reserved: Credits

    source_type: CreditSourceType
    source_id: str | None
    description: str | None
    occurred_at: datetime

    def __post_init__(self) -> None:
        if isinstance(self.delta, bool) or not isinstance(self.delta, int):
            raise InvalidCreditLedgerEntryError(
                "Credit ledger entry delta must be an integer."
            )

        if self.delta == 0:
            raise InvalidCreditLedgerEntryError(
                "Credit ledger entry delta cannot be zero."
            )
