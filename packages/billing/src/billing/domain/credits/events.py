from dataclasses import dataclass
from datetime import datetime

from billing.domain.credits.value_objects import (
    ConsumptionId,
    Credits,
    GrantId,
    ProductCode,
)
from billing.domain.shared.domain_event import DomainEvent
from billing.domain.shared.enums import CreditSource
from billing.domain.shared.ids import (
    ReferenceId,
    RequestId,
    UserId,
)


@dataclass(frozen=True, slots=True)
class CreditsGranted(DomainEvent):
    # account_id: CreditAccountId
    grant_id: GrantId
    user_id: UserId
    source: CreditSource
    credits: Credits
    expires_at: datetime | None
    reference_id: ReferenceId
    request_id: RequestId | None = None


@dataclass(frozen=True, slots=True)
class CreditsConsumed(DomainEvent):
    # account_id: CreditAccountId
    user_id: UserId
    consumption_id: ConsumptionId
    product_code: ProductCode
    credits: Credits
    reference_id: ReferenceId
    request_id: RequestId | None = None

    # cost: Credits
    # allocations: tuple[ConsumptionAllocation, ...]
    # occurred_at: datetime
    # request_id: RequestId | None = None
    # metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CreditsExpired(DomainEvent):
    grant_id: GrantId
    user_id: UserId
    expired_credits: Credits
    expired_at: datetime
