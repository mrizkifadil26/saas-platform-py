from dataclasses import dataclass

from billing.shared.domain.value_objects.base_id import BaseId


@dataclass(frozen=True, slots=True)
class CreditLedgerEntryId(BaseId):
    """Value object representing the unique identifier for a credit ledger entry."""

    pass
