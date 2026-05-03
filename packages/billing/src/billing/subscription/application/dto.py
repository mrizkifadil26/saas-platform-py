from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class SubscriptionItemDTO:
    item_id: str
    product_code: str
    feature_code: str
    quantity: int


@dataclass(frozen=True, slots=True)
class SubscriptionDTO:
    subscription_id: str
    # TODO: should use customer_id instead of user_id
    user_id: str
    # TODO: later we should use plan_id instead of plan_code, but for now we need to keep plan_code for backward compatibility with existing subscriptions
    # plan_id=str(subscription.plan_id),
    plan_code: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    provider_subscription_id: str | None
    items: tuple[SubscriptionItemDTO, ...] = ()
    # TODO: still confused about this field, should we put it here?
    # last_granted_period_start: datetime | None


# @dataclass(frozen=True, slots=True)
# class SubscriptionGrantDTO:
#     subscription_id: str
#     user_id: str
#     plan_code: str
#     grant_id: str
#     credits: Credits
#     expires_at: datetime
#     request_id: str | None


# def to_subscription_grant_dto(
#     result,
# ) -> SubscriptionGrantDTO:
#     return SubscriptionGrantDTO(
#         subscription_id=str(result.subscription.subscription_id),
#         user_id=str(result.subscription.user_id),
#         plan_code=str(result.plan.code),
#         grant_id=str(result.grant.grant_id),
#         credits=result.grant.granted_credits,
#         expires_at=result.grant.expires_at,
#         request_id=str(result.grant.request_id) if result.grant.request_id else None,
#     )
