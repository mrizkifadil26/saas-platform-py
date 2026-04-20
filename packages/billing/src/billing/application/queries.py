from dataclasses import dataclass, field
from datetime import datetime

from billing.application.dto import (
    BillingSummaryDTO,
    WalletDTO,
)
from billing.application.ports import Clock, SystemClock
from billing.domain.credits.repositories import (
    CreditGrantRepository,
)
from billing.domain.shared.ids import UserId
from billing.domain.subscription.repositories import (
    SubscriptionRepository,
)
from billing.domain.wallet.domain_services import (
    build_wallet,
    get_billing_summary,
)


@dataclass(frozen=True, slots=True)
class BillingQueryService:
    grant_repository: CreditGrantRepository
    subscription_repository: SubscriptionRepository
    clock: Clock = field(default_factory=SystemClock)

    def get_wallet(
        self,
        user_id: UserId,
        *,
        now: datetime | None = None,
    ) -> WalletDTO:
        effective_now = now or self.clock.now()
        wallet = build_wallet(
            user_id=user_id,
            grants=self.grant_repository.list_active_for_user(
                user_id
            ),
            now=effective_now,
        )
        return WalletDTO(
            user_id=wallet.user_id,
            total_credits=wallet.total_credits,
            subscription_credits=wallet.subscription_credits,
            payg_credits=wallet.payg_credits,
        )

    def get_billing_summary(
        self,
        user_id: UserId,
        *,
        now: datetime | None = None,
    ) -> BillingSummaryDTO:
        effective_now = now or self.clock.now()
        summary = get_billing_summary(
            user_id=user_id,
            grants=self.grant_repository.list_active_for_user(
                user_id
            ),
            subscription=self.subscription_repository.get_active_for_user(
                user_id
            ),
            now=effective_now,
        )
        return BillingSummaryDTO(
            user_id=summary.user_id,
            total_credits=summary.total_credits,
            subscription_credits=summary.subscription_credits,
            payg_credits=summary.payg_credits,
            subscription_status=summary.subscription_status,
            subscription_plan_code=summary.subscription_plan_code,
            subscription_period_end=summary.current_period_end,
        )
