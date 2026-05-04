from billing.subscription.application.dto import (
    SubscriptionDTO,
    SubscriptionItemDTO,
)
from billing.subscription.domain.subscription import Subscription
from billing.subscription.domain.subscription_item import SubscriptionItem


class SubscriptionItemMapper:
    @staticmethod
    def to_dto(item: SubscriptionItem) -> SubscriptionItemDTO:
        return SubscriptionItemDTO(
            item_id=str(item.item_id),
            product_code=str(item.product_code),
            feature_code=str(item.feature_code),
            quantity=item.quantity,
        )


class SubscriptionMapper:
    @classmethod
    def to_dto(cls, subscription: Subscription) -> SubscriptionDTO:
        return SubscriptionDTO(
            subscription_id=str(subscription.subscription_id),
            user_id=str(subscription.user_id),
            plan_code=str(subscription.plan_code),
            status=subscription.status.value,
            current_period_start=subscription.current_period_start,
            current_period_end=subscription.current_period_end,
            cancel_at_period_end=subscription.cancel_at_period_end,
            provider_subscription_id=subscription.provider_subscription_id,
            items=tuple(
                SubscriptionItemMapper.to_dto(item) for item in subscription.items
            ),
        )
