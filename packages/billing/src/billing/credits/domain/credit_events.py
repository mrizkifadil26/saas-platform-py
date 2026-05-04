from dataclasses import dataclass
from datetime import datetime

from billing.credits.domain.credit_source_type import CreditSourceType
from billing.credits.domain.value_objects.credit_account_id import CreditAccountId
from billing.credits.domain.value_objects.credit_grant_id import CreditGrantId
from billing.credits.domain.value_objects.credits import Credits
from billing.shared.domain.domain_event import DomainEvent
from billing.shared.domain.value_objects.user_id import UserId


@dataclass(frozen=True, slots=True)
class CreditAccountCreated(DomainEvent):
    credit_account_id: CreditAccountId
    # TODO: Replace user_id with customer_id once billing is decoupled from auth/user domain
    #       This event should reference a billing/customer aggregate, not an auth concept.
    user_id: UserId


@dataclass(frozen=True, slots=True)
class CreditsGranted(DomainEvent):
    credit_account_id: CreditAccountId
    grant_id: CreditGrantId
    amount: Credits
    source_type: CreditSourceType
    source_id: str | None = None
    expires_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class CreditsExpired(DomainEvent):
    credit_account_id: CreditAccountId
    grant_id: CreditGrantId
    amount: Credits
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class CreditsReserved(DomainEvent):
    credit_account_id: CreditAccountId
    amount: Credits
    source_id: str | None


@dataclass(frozen=True, slots=True)
class ReservedCreditsConsumed(DomainEvent):
    credit_account_id: CreditAccountId
    amount: Credits
    source_id: str | None


@dataclass(frozen=True, slots=True)
class ReservedCreditsReleased(DomainEvent):
    credit_account_id: CreditAccountId
    amount: Credits
    source_id: str | None
