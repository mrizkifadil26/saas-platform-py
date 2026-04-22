from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from billing.domain.credits.events import (
    CreditsConsumed,
    CreditsExpired,
    CreditsGranted,
)
from billing.domain.credits.exceptions import (
    GrantNotActive,
    GrantNotAvailable,
    InsufficientCredits,
    InvalidCreditsAmount,
)
from billing.domain.credits.value_objects import (
    ConsumptionId,
    Credits,
    GrantId,
    ProductCode,
)
from billing.domain.shared.enums import (
    CreditSource,
    GrantStatus,
)
from billing.domain.shared.ids import (
    ReferenceId,
    RequestId,
    UserId,
)


@dataclass(slots=True)
class CreditGrant:
    # granted_credits: Credits
    # remaining_credits: Credits
    # created_at: datetime
    # plan_code: PlanCode | None = None

    grant_id: GrantId
    user_id: UserId

    source: CreditSource
    total_credits: Credits
    consumed_credits: Credits

    reference_id: ReferenceId
    granted_at: datetime
    expires_at: datetime | None = None
    request_id: RequestId | None = None

    status: GrantStatus = GrantStatus.ACTIVE
    metadata: dict[str, str] = field(default_factory=dict)
    _events: list[object] = field(
        default_factory=list, init=False, repr=False
    )

    def __post_init__(self) -> None:
        if int(self.total_credits) <= 0:
            raise InvalidCreditsAmount(
                "grant must be positive"
            )
        if int(self.consumed_credits) < 0:
            raise InvalidCreditsAmount(
                "consumed credits cannot be negative"
            )
        if int(self.consumed_credits) > int(
            self.total_credits
        ):
            raise InvalidCreditsAmount(
                "consumed credits cannot exceed total"
            )

    @property
    def available_credits(self) -> Credits:
        return Credits(
            int(self.total_credits)
            - int(self.consumed_credits)
        )

    @property
    def events(self) -> tuple[object, ...]:
        return tuple(self._events)

    def pull_events(self) -> list[object]:
        events = list(self._events)
        self._events.clear()
        return events

    @classmethod
    def create(
        cls,
        *,
        grant_id: GrantId,
        user_id: UserId,
        source: CreditSource,
        credits: Credits,
        reference_id: ReferenceId,
        granted_at: datetime,
        expires_at: datetime | None = None,
        request_id: RequestId | None = None,
    ) -> CreditGrant:
        grant = cls(
            grant_id=grant_id,
            user_id=user_id,
            source=source,
            total_credits=credits,
            consumed_credits=Credits(0),
            reference_id=reference_id,
            granted_at=granted_at,
            expires_at=expires_at,
            request_id=request_id,
            status=GrantStatus.ACTIVE,
        )
        grant._events.append(
            CreditsGranted(
                grant_id=grant.grant_id,
                user_id=grant.user_id,
                source=grant.source,
                credits=grant.total_credits,
                expires_at=grant.expires_at,
                reference_id=grant.reference_id,
                request_id=grant.request_id,
            )
        )
        return grant

    def is_active_at(self, at: datetime) -> bool:
        if int(self.available_credits) <= 0:
            return False
        if (
            self.expires_at is not None
            and at >= self.expires_at
        ):
            return False
        return True

    def consume(
        self, credits: Credits, at: datetime
    ) -> None:
        if int(credits) <= 0:
            raise InvalidCreditsAmount(
                "consumption must be positive"
            )
        if not self.is_active_at(at):
            raise GrantNotAvailable("grant is not active")
        if int(credits) > int(self.available_credits):
            raise InsufficientCredits(
                "not enough remaining credits in grant"
            )
        self.consumed_credits = Credits(
            int(self.consumed_credits) + int(credits)
        )

    # def consume(
    #     self,
    #     *,
    #     consumption_id: ConsumptionId,
    #     product_code: ProductCode,
    #     credits: Credits,
    #     consumed_at: datetime,
    #     reference_id: ReferenceId,
    #     request_id: RequestId | None = None,
    # ) -> CreditConsumption:
    #     if int(credits) <= 0:
    #         raise InvalidCreditsAmount(
    #             "consumption credits must be positive"
    #         )
    #     if not self.is_active_at(consumed_at):
    #         raise GrantNotActive(
    #             "credit grant is not active at requested time"
    #         )
    #     if int(credits) > int(self.available_credits):
    #         raise InsufficientCredits(
    #             "requested credits exceed grant available credits"
    #         )

    #     self.consumed_credits = Credits(
    #         int(self.consumed_credits) + int(credits)
    #     )
    #     if int(self.available_credits) == 0:
    #         self.status = GrantStatus.FULLY_CONSUMED

    #     consumption = CreditConsumption(
    #         consumption_id=consumption_id,
    #         grant_id=self.grant_id,
    #         # user_id=self.user_id,
    #         product_code=product_code,
    #         credits=credits,
    #         consumed_at=consumed_at,
    #         reference_id=reference_id,
    #         request_id=request_id,
    #     )

    #     event = CreditsConsumed(
    #         consumption_id=consumption.consumption_id,
    #         # grant_id=self.grant_id,
    #         user_id=self.user_id,
    #         product_code=consumption.product_code,
    #         credits=consumption.credits,
    #         reference_id=consumption.reference_id,
    #         request_id=consumption.request_id,
    #     )
    #     self._events.append(event)

    #     return consumption
    # self.remaining_credits = (
    #     self.remaining_credits - credits
    # )

    # return ConsumptionAllocation(
    #     grant_id=self.grant_id,
    #     credits=amount,
    # )

    # def is_expired(self, now: datetime) -> bool:
    #     return (
    #         self.expires_at is not None
    #         and self.expires_at < now
    #     )

    # def is_depleted(self) -> bool:
    #     return self.remaining_credits.is_zero()

    # def is_active(self, now: datetime) -> bool:
    #     return (
    #         not self.is_expired(now)
    #         and not self.is_depleted()
    #     )

    def expire(self, at: datetime) -> Credits:
        if self.status != GrantStatus.ACTIVE:
            return Credits(0)

        if self.expires_at is None or at < self.expires_at:
            return Credits(0)

        remaining = self.available_credits
        if int(remaining) <= 0:
            self.status = GrantStatus.FULLY_CONSUMED
            return Credits(0)

        self.status = GrantStatus.EXPIRED

        event = CreditsExpired(
            grant_id=self.grant_id,
            user_id=self.user_id,
            expired_credits=remaining,
            expired_at=at,
        )
        self._events.append(event)

        return remaining


# @dataclass(eq=True, slots=True)
@dataclass(frozen=True, slots=True)
class CreditConsumption:
    # user_id: UserId
    # cost: Credits
    # allocations: tuple[ConsumptionAllocation, ...]
    # metadata: dict[str, str] = field(default_factory=dict)
    consumption_id: ConsumptionId
    grant_id: GrantId
    product_code: ProductCode
    credits: Credits
    consumed_at: datetime
    reference_id: ReferenceId
    request_id: RequestId | None = None

    def __post_init__(self) -> None:
        if int(self.credits) <= 0:
            raise InvalidCreditsAmount(
                "consumption credits must be positive"
            )
