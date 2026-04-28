from dataclasses import dataclass
from datetime import datetime

from billing.credits.domain.credit_source_type import CreditSourceType
from billing.credits.domain.value_objects.credit_account_id import CreditAccountId
from billing.credits.domain.value_objects.credit_grant_id import CreditGrantId
from billing.shared.domain.domain_event import DomainEvent
from billing.shared.domain.value_objects.user_id import UserId


@dataclass(frozen=True, slots=True)
class CreditAccountCreated(DomainEvent):
    credit_account_id: CreditAccountId
    # TODO: later we need to use customer_Id instead of user_id, but for now we can use user_id as a placeholder
    user_id: UserId


@dataclass(frozen=True, slots=True)
class CreditsGranted(DomainEvent):
    credit_account_id: CreditAccountId
    grant_id: CreditGrantId
    # TODO: should use Credits value object instead of int for amount, but for simplicity we can use int for now
    amount: int
    source_type: CreditSourceType
    source_id: str | None = None
    expires_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class CreditsReserved(DomainEvent):
    account_id: CreditAccountId
    # TODO: should use Credits value object instead of int for amount, but for simplicity we can use int for now
    amount: int
    source_id: str | None


@dataclass(frozen=True, slots=True)
class ReservedCreditsConsumed(DomainEvent):
    account_id: CreditAccountId
    # TODO: should use Credits value object instead of int for amount, but for simplicity we can use int for now
    amount: int
    source_id: str | None


@dataclass(frozen=True, slots=True)
class ReservedCreditsReleased(DomainEvent):
    account_id: CreditAccountId
    # TODO: should use Credits value object instead of int for amount, but for simplicity we can use int for now
    amount: int
    reference_id: str | None


@dataclass(frozen=True, slots=True)
class CreditsExpired(DomainEvent):
    credit_account_id: CreditAccountId
    # TODO: should use Credits value object instead of int for amount, but for simplicity we can use int for now
    amount: int
