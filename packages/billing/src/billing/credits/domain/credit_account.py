from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from billing.credits.domain.credit_balance import CreditBalance
from billing.credits.domain.credit_events import (
    CreditAccountCreated,
    CreditsExpired,
    CreditsGranted,
    CreditsReserved,
    ReservedCreditsConsumed,
    ReservedCreditsReleased,
)
from billing.credits.domain.credit_grant import CreditGrant
from billing.credits.domain.credit_ledger_entry import CreditLedgerEntry
from billing.credits.domain.credit_source_type import CreditSourceType
from billing.credits.domain.exceptions import CreditBalanceInconsistentError
from billing.credits.domain.value_objects.credit_account_id import CreditAccountId
from billing.credits.domain.value_objects.credit_grant_id import CreditGrantId
from billing.credits.domain.value_objects.credit_ledger_entry_id import (
    CreditLedgerEntryId,
)
from billing.credits.domain.value_objects.credits import Credits
from billing.shared.domain.aggregate_root import AggregateRoot
from billing.shared.domain.value_objects.user_id import UserId
from billing.subscription.domain.value_objects.subscription_id import SubscriptionId


@dataclass(slots=True)
class CreditAccount(AggregateRoot[CreditAccountId]):
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
        account = cls(
            id=id,
            user_id=user_id,
            balance=CreditBalance.zero(),
        )

        event = CreditAccountCreated(
            credit_account_id=id,
            user_id=user_id,
        )
        account.record_event(event)

        return account

    def grant(
        self,
        *,
        grant_id: CreditGrantId,
        amount: Credits,
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
            amount=int(amount),
            source_type=source_type,
            source_id=source_id,
            description=description,
            occurred_at=occurred_at,
        )

        event = CreditsGranted(
            credit_account_id=self.id,
            grant_id=grant_id,
            amount=int(amount),
            source_type=source_type,
            source_id=source_id,
            expires_at=expires_at,
            occurred_at=occurred_at,
        )

        self.record_event(event)

    def reserve(
        self,
        *,
        amount: Credits,
        occurred_at: datetime,
        source_id: str | None = None,
        description: str | None = None,
    ) -> None:
        self.balance = self.balance.reserve(amount)

        self._record_entry(
            amount=-int(amount),
            source_type=CreditSourceType.RESERVATION,
            source_id=source_id,
            description=description,
            occurred_at=occurred_at,
        )

        event = CreditsReserved(
            credit_account_id=self.id,
            amount=int(amount),
            source_id=source_id,
            occurred_at=occurred_at,
        )

        self.record_event(event)

    def consume_reserved(
        self,
        *,
        amount: Credits,
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

        if remaining_to_consume.is_positive():
            raise CreditBalanceInconsistentError(
                "Grant balances are inconsistent with reserved balance"
            )

        self.grants = updated_grants

        self._record_entry(
            amount=-int(amount),
            source_type=CreditSourceType.USAGE_CONSUMPTION,
            source_id=source_id,
            description=description,
            occurred_at=occurred_at,
        )

        event = ReservedCreditsConsumed(
            credit_account_id=self.id,
            amount=int(amount),
            source_id=source_id,
            occurred_at=occurred_at,
        )
        self.record_event(event)

    def release_reserved(
        self,
        *,
        amount: Credits,
        occurred_at: datetime,
        source_id: str | None = None,
        description: str | None = None,
    ) -> None:
        self.balance = self.balance.release_reserved(amount)

        self._record_entry(
            amount=int(amount),
            source_type=CreditSourceType.RESERVATION_RELEASE,
            source_id=source_id,
            description=description,
            occurred_at=occurred_at,
        )

        event = ReservedCreditsReleased(
            credit_account_id=self.id,
            amount=int(amount),
            source_id=source_id,
            occurred_at=occurred_at,
        )

        self.record_event(event)

    def expire_grants(
        self,
        *,
        occurred_at: datetime,
        description: str | None = None,
    ) -> Credits:
        expired_amount = Credits.zero()
        updated_grants: list[CreditGrant] = []

        for grant in self.grants:
            if grant.is_expired_at(occurred_at) and grant.remaining.is_positive():
                expired_amount = expired_amount + grant.remaining
                updated_grants.append(grant.expire(at=occurred_at))
            else:
                updated_grants.append(grant)

        if expired_amount.is_zero():
            self.grants = updated_grants
            return Credits.zero()

        self.balance = self.balance.subtract_available(expired_amount)
        self.grants = updated_grants

        self._record_entry(
            amount=-int(expired_amount),
            source_type=CreditSourceType.EXPIRATION,
            source_id=None,
            description=description,
            occurred_at=occurred_at,
        )

        event = CreditsExpired(
            credit_account_id=self.id,
            amount=int(expired_amount),
            occurred_at=occurred_at,
        )
        self.record_event(event)

        return expired_amount

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
            id=CreditLedgerEntryId(uuid4().hex),
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
