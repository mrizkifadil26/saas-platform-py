from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from billing.credits.domain.credit_balance import CreditBalance
from billing.credits.domain.credit_grant import CreditGrant
from billing.credits.domain.credit_ledger_entry import CreditLedgerEntry
from billing.credits.domain.credit_source_type import CreditSourceType
from billing.credits.domain.exceptions import CreditBalanceInconsistentError
from billing.credits.domain.value_objects.credit_account_id import CreditAccountId
from billing.credits.domain.value_objects.credit_grant_id import CreditGrantId
from billing.credits.domain.value_objects.credit_ledger_entry_id import (
    CreditLedgerEntryId,
)
from billing.shared.domain.value_objects.user_id import UserId


@dataclass(slots=True)
class CreditAccount:
    id: CreditAccountId
    # TODO: later we need to use customer_Id instead of user_id, but for now we can use user_id as a placeholder
    user_id: UserId
    balance: CreditBalance
    grants: list[CreditGrant] = field(default_factory=list)
    ledger_entries: list[CreditLedgerEntry] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        *,
        id: CreditAccountId,
        user_id: UserId,
    ) -> CreditAccount:
        return cls(
            id=id,
            user_id=user_id,
            balance=CreditBalance(available=0, reserved=0),
        )

    def grant(
        self,
        *,
        grant_id: CreditGrantId,
        amount: int,
        occurred_at: datetime,
        expires_at: datetime | None = None,
        source_type: CreditSourceType = CreditSourceType.SUBSCRIPTION_GRANT,
        source_id: str | None = None,
        description: str | None = None,
    ) -> None:
        grant = CreditGrant(
            id=grant_id,
            credit_account_id=self.id,
            amount=amount,
            remaining=amount,
            granted_at=occurred_at,
            expires_at=expires_at,
            source_id=source_id,
        )

        self.grants.append(grant)
        self.balance = self.balance.add(amount)

        self._record_entry(
            amount=amount,
            source_type=source_type,
            source_id=source_id,
            description=description,
            occurred_at=occurred_at,
        )

    def reserve(
        self,
        *,
        amount: int,
        occurred_at: datetime,
        source_id: str | None = None,
        description: str | None = None,
    ) -> None:
        self.balance = self.balance.reserve(amount)

        self._record_entry(
            amount=-amount,
            source_type=CreditSourceType.RESERVATION,
            source_id=source_id,
            description=description,
            occurred_at=occurred_at,
        )

    def consume_reserved(
        self,
        *,
        amount: int,
        occurred_at: datetime,
        source_id: str | None = None,
        description: str | None = None,
    ) -> None:
        self.balance = self.balance.consume_reserved(amount)

        remaining_to_consume = amount
        updated_grants: list[CreditGrant] = []

        for grant in sorted(
            self.grants,
            key=lambda grant: (
                grant.expires_at or datetime.max.replace(tzinfo=occurred_at.tzinfo)
            ),
        ):
            if remaining_to_consume == 0:
                updated_grants.append(grant)
                continue

            if grant.remaining == 0:
                updated_grants.append(grant)
                continue

            consumed = min(grant.remaining, remaining_to_consume)
            updated_grants.append(grant.consume(consumed))
            remaining_to_consume -= consumed

        if remaining_to_consume > 0:
            raise CreditBalanceInconsistentError(
                "Grant balances are inconsistent with reserved balance"
            )

        self.grants = updated_grants

        self._record_entry(
            amount=-amount,
            source_type=CreditSourceType.USAGE_CONSUMPTION,
            source_id=source_id,
            description=description,
            occurred_at=occurred_at,
        )

    def release_reserved(
        self,
        *,
        amount: int,
        occurred_at: datetime,
        source_id: str | None = None,
        description: str | None = None,
    ) -> None:
        self.balance = self.balance.release_reserved(amount)

        self._record_entry(
            amount=amount,
            source_type=CreditSourceType.RESERVATION_RELEASE,
            source_id=source_id,
            description=description,
            occurred_at=occurred_at,
        )

    def _record_entry(
        self,
        *,
        amount: int,
        source_type: CreditSourceType,
        source_id: str | None,
        description: str | None,
        occurred_at: datetime,
    ) -> None:
        entry = CreditLedgerEntry(
            # TODO: generate a proper UUID for the ledger entry
            id=CreditLedgerEntryId(UUID(int=0).hex),
            credit_account_id=self.id,
            amount=amount,
            balance_after_available=self.balance.available,
            balance_after_reserved=self.balance.reserved,
            source_type=source_type,
            source_id=source_id,
            description=description,
            occurred_at=occurred_at,
        )

        self.ledger_entries.append(entry)
