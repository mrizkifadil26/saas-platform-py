from billing.subscription.application.commands import (
    CreateSubscriptionItemCommand,
)
from billing.subscription.application.dto import (
    SubscriptionDTO,
    SubscriptionItemDTO,
)
from billing.subscription.domain.subscription import Subscription
from billing.subscription.domain.subscription_item import SubscriptionItem
from billing.subscription.domain.value_objects.feature_code import FeatureCode
from billing.subscription.domain.value_objects.product_code import ProductCode
from billing.subscription.domain.value_objects.subscription_item_id import (
    SubscriptionItemId,
)


class SubscriptionMapper:
    @staticmethod
    def command_item_to_domain(
        command: CreateSubscriptionItemCommand,
    ) -> SubscriptionItem:
        return SubscriptionItem(
            item_id=SubscriptionItemId(command.item_id),
            product_code=ProductCode(command.product_code),
            feature_code=FeatureCode(command.feature_code),
            quantity=command.quantity,
        )

    @staticmethod
    def dto_item_to_domain(dto: SubscriptionItemDTO) -> SubscriptionItem:
        return SubscriptionItem(
            item_id=SubscriptionItemId(dto.item_id),
            product_code=ProductCode(dto.product_code),
            feature_code=FeatureCode(dto.feature_code),
            quantity=dto.quantity,
        )

    @staticmethod
    def domain_item_to_dto(item: SubscriptionItem) -> SubscriptionItemDTO:
        return SubscriptionItemDTO(
            item_id=str(item.item_id),
            product_code=str(item.product_code),
            feature_code=str(item.feature_code),
            quantity=item.quantity,
        )

    @classmethod
    def domain_to_dto(cls, subscription: Subscription) -> SubscriptionDTO:
        return SubscriptionDTO(
            subscription_id=str(subscription.subscription_id),
            user_id=str(subscription.user_id),
            # TODO: later we should use plan_id instead of plan_code, but for now we need to keep plan_code for backward compatibility with existing subscriptions
            # plan_id=str(subscription.plan_id),
            plan_code=str(subscription.plan_code),
            status=subscription.status,
            current_period_start=subscription.current_period_start,
            current_period_end=subscription.current_period_end,
            cancel_at_period_end=subscription.cancel_at_period_end,
            provider_subscription_id=subscription.provider_subscription_id,
            items=tuple(cls.domain_item_to_dto(item) for item in subscription.items),
        )
