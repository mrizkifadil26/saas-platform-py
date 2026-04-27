from billing.subscription.interfaces.schemas import (
    SubscriptionItemResponse,
    SubscriptionResponse,
)

from billing.subscription.application.dto import SubscriptionDTO


def to_response(dto: SubscriptionDTO) -> SubscriptionResponse:
    return SubscriptionResponse(
        subscription_id=dto.subscription_id,
        # TODO: should replace it with customer_id
        user_id=dto.user_id,
        plan_id=dto.plan_id,
        status=dto.status,
        current_period_start=dto.current_period_start,
        current_period_end=dto.current_period_end,
        cancel_at_period_end=dto.cancel_at_period_end,
        provider_subscription_id=dto.provider_subscription_id,
        items=[
            SubscriptionItemResponse(
                item_id=item.item_id,
                product_code=item.product_code,
                feature_code=item.feature_code,
                quantity=item.quantity,
            )
            for item in dto.items
        ],
    )
