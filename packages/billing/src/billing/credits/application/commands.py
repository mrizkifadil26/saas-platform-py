from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from billing.credits.domain.credit_source_type import CreditSourceType
from billing.credits.domain.value_objects.credit_account_id import CreditAccountId
from billing.credits.domain.value_objects.credit_grant_id import CreditGrantId
from billing.shared.domain.value_objects.user_id import UserId


@dataclass(frozen=True, slots=True)
class CreateCreditAccountCommand:
    credit_account_id: CreditAccountId
    # TODO: should use customer_id instead of user_id
    user_id: UserId


@dataclass(frozen=True, slots=True)
class GrantCreditsCommand:
    # TODO: should use customer_id instead of user_id
    user_id: UserId
    grant_id: CreditGrantId
    amount: int
    source_type: CreditSourceType = CreditSourceType.SUBSCRIPTION_GRANT
    source_id: str | None = None
    description: str | None = None
    expires_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class PurchaseCreditsCommand:
    # TODO: should use customer_id instead of user_id
    user_id: UserId
    grant_id: CreditGrantId
    amount: int
    source_id: str | None = None
    description: str | None = None
    expires_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class ReserveCreditsCommand:
    # TODO: should use customer_id instead of user_id
    user_id: UserId
    amount: int
    source_id: str | None = None
    description: str | None = None


@dataclass(frozen=True, slots=True)
class ConsumeReservedCreditsCommand:
    # TODO: should use customer_id instead of user_id
    user_id: UserId
    amount: int
    source_id: str | None = None
    description: str | None = None


@dataclass(frozen=True, slots=True)
class ReleaseReservedCreditsCommand:
    # TODO: should use customer_id instead of user_id
    user_id: UserId
    amount: int
    source_id: str | None = None
    description: str | None = None


@dataclass(frozen=True, slots=True)
class ExpireCreditsCommand:
    # TODO: should use customer_id instead of user_id
    user_id: UserId
    description: str | None = None
