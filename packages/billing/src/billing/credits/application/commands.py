from dataclasses import dataclass
from datetime import datetime

from billing.credits.domain.credit_source_type import CreditSourceType
from billing.shared.domain.value_objects.user_id import UserId

# NOTE:
# Billing currently uses user_id as a placeholder identity.
# This should be replaced with customer_id once a proper billing/customer
# aggregate exists and is decoupled from the auth/user domain.


@dataclass(frozen=True, slots=True)
class CreateCreditAccountCommand:
    user_id: UserId


@dataclass(frozen=True, slots=True)
class GrantCreditsCommand:
    user_id: UserId
    amount: int
    source_type: CreditSourceType = CreditSourceType.SUBSCRIPTION_GRANT
    source_id: str | None = None
    description: str | None = None
    expires_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class ExpireCreditsCommand:
    user_id: UserId
    description: str | None = None


@dataclass(frozen=True, slots=True)
class ReserveCreditsCommand:
    user_id: UserId
    amount: int
    source_id: str | None = None
    description: str | None = None


@dataclass(frozen=True, slots=True)
class ConsumeReservedCreditsCommand:
    user_id: UserId
    amount: int
    source_id: str | None = None
    description: str | None = None


@dataclass(frozen=True, slots=True)
class ReleaseReservedCreditsCommand:
    user_id: UserId
    amount: int
    source_id: str | None = None
    description: str | None = None
