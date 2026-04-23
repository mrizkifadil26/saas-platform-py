from dataclasses import dataclass
from datetime import datetime

from billing.credits.domain.value_objects.credits import Credits
from billing.subscription.domain.subscription_status import SubscriptionStatus


@dataclass(frozen=True, slots=True)
class SubscriptionDTO:
    subscription_id: str
    user_id: str
    plan_code: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    provider_subscription_id: str | None
    last_granted_period_start: datetime | None


@dataclass(frozen=True, slots=True)
class SubscriptionGrantDTO:
    subscription_id: str
    user_id: str
    plan_code: str
    grant_id: str
    credits: Credits
    expires_at: datetime
    request_id: str | None


def to_subscription_dto(subscription) -> SubscriptionDTO:
    return SubscriptionDTO(
        subscription_id=str(subscription.subscription_id),
        user_id=str(subscription.user_id),
        plan_code=str(subscription.plan_code),
        status=subscription.status,
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        cancel_at_period_end=subscription.cancel_at_period_end,
        provider_subscription_id=subscription.provider_subscription_id,
        last_granted_period_start=subscription.last_granted_period_start,
    )


def to_subscription_grant_dto(
    result,
) -> SubscriptionGrantDTO:
    return SubscriptionGrantDTO(
        subscription_id=str(result.subscription.subscription_id),
        user_id=str(result.subscription.user_id),
        plan_code=str(result.plan.code),
        grant_id=str(result.grant.grant_id),
        credits=result.grant.granted_credits,
        expires_at=result.grant.expires_at,
        request_id=str(result.grant.request_id) if result.grant.request_id else None,
    )
