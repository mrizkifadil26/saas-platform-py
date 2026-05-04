from dataclasses import dataclass
from datetime import datetime

from billing.credits.domain.credit_source_type import CreditSourceType
from billing.credits.domain.value_objects.credit_account_id import CreditAccountId
from billing.credits.domain.value_objects.credit_grant_id import CreditGrantId
from billing.credits.domain.value_objects.credit_ledger_entry_id import (
    CreditLedgerEntryId,
)
from billing.shared.domain.value_objects.user_id import UserId


@dataclass(frozen=True, slots=True)
class CreditBalanceDTO:
    available: int
    reserved: int
    total: int


@dataclass(frozen=True, slots=True)
class CreditAccountDTO:
    id: CreditAccountId
    user_id: UserId
    balance: CreditBalanceDTO
    grants: tuple[CreditGrantDTO, ...]
    ledger_entries: tuple[CreditLedgerEntryDTO, ...]


@dataclass(frozen=True, slots=True)
class CreditGrantDTO:
    id: CreditGrantId
    credit_account_id: CreditAccountId
    amount: int
    remaining: int
    granted_at: datetime
    expires_at: datetime | None
    source_id: str | None


@dataclass(frozen=True, slots=True)
class CreditLedgerEntryDTO:
    id: CreditLedgerEntryId
    credit_account_id: CreditAccountId
    delta: int
    balance_after_available: int
    balance_after_reserved: int
    source_type: CreditSourceType
    source_id: str | None
    description: str | None
    occurred_at: datetime
