from dataclasses import dataclass, field
from datetime import datetime

from billing.domain.credits.entities import (
    CreditConsumption,
    CreditGrant,
)
from billing.domain.credits.events import (
    CreditGrantAdded,
    CreditGrantExpired,
    CreditsConsumed,
)
from billing.domain.credits.exceptions import (
    DuplicateReference,
    InsufficientCredits,
)
from billing.domain.credits.value_objects import (
    ConsumptionId,
    CreditAccountId,
    Credits,
    GrantId,
    ProductCode,
)
from billing.domain.shared.enums import CreditSource
from billing.domain.shared.ids import (
    ReferenceId,
    RequestId,
    UserId,
)


@dataclass(slots=True)
class CreditAccount:
    id: CreditAccountId
    user_id: UserId
    grants: list[CreditGrant] = field(default_factory=list)
    _events: list[object] = field(
        default_factory=list, init=False, repr=False
    )

    @property
    def events(self) -> tuple[object, ...]:
        return tuple(self._events)

    def pull_events(self) -> list[object]:
        events = list(self._events)
        self._events.clear()
        return events

    def total_available(self, at: datetime) -> Credits:
        total = sum(
            int(grant.remaining_credits)
            for grant in self.grants
            if grant.is_active_at(at)
        )
        return Credits(total)

    def has_reference(
        self,
        reference_id: ReferenceId,
    ) -> bool:
        return any(
            grant.reference_id == reference_id
            for grant in self.grants
        )

    def add_grant(
        self,
        *,
        grant_id: GrantId,
        source: CreditSource,
        credits: Credits,
        reference_id: ReferenceId,
        granted_at: datetime,
        expires_at: datetime | None,
    ) -> CreditGrant:
        if self.has_reference(reference_id):
            raise DuplicateReference(
                f"grant reference already exists: {reference_id}"
            )

        grant = CreditGrant(
            grant_id=grant_id,
            source=source,
            total_credits=credits,
            consumed_credits=Credits(0),
            reference_id=reference_id,
            granted_at=granted_at,
            expires_at=expires_at,
        )
        self.grants.append(grant)
        self._events.append(
            CreditGrantAdded(
                account_id=self.id,
                user_id=self.user_id,
                grant_id=grant.grant_id,
                source=grant.source,
                credits=grant.total_credits,
                expires_at=grant.expires_at,
            )
        )
        return grant

    def consume(
        self,
        *,
        consumption_id: ConsumptionId,
        product_code: ProductCode,
        credits: Credits,
        consumed_at: datetime,
        reference_id: ReferenceId,
        request_id: RequestId | None = None,
    ) -> list[CreditConsumption]:
        if int(self.total_available(consumed_at)) < int(
            credits
        ):
            raise InsufficientCredits(
                "not enough available credits"
            )

        remaining = int(credits)
        consumptions: list[CreditConsumption] = []

        for grant in self._ordered_active_grants(
            consumed_at
        ):
            if remaining == 0:
                break

            spend = min(
                int(grant.remaining_credits), remaining
            )
            if spend <= 0:
                continue

            grant.consume(Credits(spend), consumed_at)

            consumption = CreditConsumption(
                consumption_id=consumption_id,
                grant_id=grant.grant_id,
                product_code=product_code,
                credits=Credits(spend),
                consumed_at=consumed_at,
                reference_id=reference_id,
                request_id=request_id,
            )
            consumptions.append(consumption)
            remaining -= spend

        if remaining != 0:
            raise InsufficientCredits(
                "failed to allocate full consumption"
            )

        self._events.append(
            CreditsConsumed(
                account_id=self.id,
                user_id=self.user_id,
                consumption_id=consumptions[
                    0
                ].consumption_id,
                product_code=product_code,
                credits=credits,
            )
        )
        return consumptions

    def expire_available_grants(
        self, at: datetime
    ) -> list[CreditGrant]:
        expired: list[CreditGrant] = []
        for grant in self.grants:
            if grant.expires_at is None:
                continue
            if at < grant.expires_at:
                continue
            if int(grant.remaining_credits) <= 0:
                continue

            remaining = grant.remaining_credits
            grant.consume(remaining, at)
            expired.append(grant)

            self._events.append(
                CreditGrantExpired(
                    account_id=self.id,
                    user_id=self.user_id,
                    grant_id=grant.grant_id,
                    credits=remaining,
                )
            )
        return expired

    def _ordered_active_grants(
        self, at: datetime
    ) -> list[CreditGrant]:
        def sort_key(grant: CreditGrant):
            expires_none = grant.expires_at is None
            source_rank = (
                0
                if grant.source == CreditSource.SUBSCRIPTION
                else 1
            )
            return (
                expires_none,
                grant.expires_at,
                source_rank,
                grant.granted_at,
            )

        active = [
            grant
            for grant in self.grants
            if grant.is_active_at(at)
        ]
        return sorted(active, key=sort_key)
