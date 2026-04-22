from dataclasses import dataclass
from datetime import datetime

from billing.domain.credits.value_objects import (
    ConsumptionId,
    CreditAccountId,
    Credits,
    GrantId,
    ProductCode,
)
from billing.domain.shared.enums import CreditSource
from billing.domain.shared.events import DomainEvent
from billing.domain.shared.ids import UserId


@dataclass(frozen=True, slots=True)
class CreditGrantAdded(DomainEvent):
    account_id: CreditAccountId
    user_id: UserId
    grant_id: GrantId
    source: CreditSource
    credits: Credits
    expires_at: datetime | None


@dataclass(frozen=True, slots=True)
class CreditsConsumed(DomainEvent):
    account_id: CreditAccountId
    user_id: UserId
    consumption_id: ConsumptionId
    product_code: ProductCode
    credits: Credits
    # cost: Credits
    # allocations: tuple[ConsumptionAllocation, ...]
    # occurred_at: datetime
    # request_id: RequestId | None = None
    # metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CreditGrantExpired(DomainEvent):
    account_id: CreditAccountId
    user_id: UserId
    grant_id: GrantId
    credits: Credits
