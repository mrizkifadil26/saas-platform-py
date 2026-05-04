import json

from billing.shared.domain.value_objects.user_id import UserId
from billing.subscription.domain.subscription import Subscription
from billing.subscription.domain.subscription_item import SubscriptionItem
from billing.subscription.domain.subscription_status import SubscriptionStatus
from billing.subscription.domain.value_objects.billing_period import BillingPeriod
from billing.subscription.domain.value_objects.feature_code import FeatureCode
from billing.subscription.domain.value_objects.plan_code import PlanCode
from billing.subscription.domain.value_objects.product_code import ProductCode
from billing.subscription.domain.value_objects.subscription_id import SubscriptionId
from billing.subscription.domain.value_objects.subscription_item_id import (
    SubscriptionItemId,
)
from billing.subscription.infrastructure.persistence.sqlalchemy.models.subscription_item_model import (
    SubscriptionItemModel,
)
from billing.subscription.infrastructure.persistence.sqlalchemy.models.subscription_model import (
    SubscriptionModel,
)


class SubscriptionORMMapper:
    @staticmethod
    def to_domain(model: SubscriptionModel) -> Subscription:
        return Subscription(
            subscription_id=SubscriptionId(model.subscription_id),
            user_id=UserId(model.user_id),
            plan_code=PlanCode(model.plan_code),
            status=SubscriptionStatus(model.status),
            billing_period=BillingPeriod(
                start_at=model.current_period_start,
                end_at=model.current_period_end,
            ),
            cancel_at_period_end=model.cancel_at_period_end,
            provider_subscription_id=model.provider_subscription_id,
            last_granted_period_start=model.last_granted_period_start,
            metadata=json.loads(model.metadata_json) if model.metadata_json else {},
            items=tuple(
                SubscriptionItem(
                    item_id=SubscriptionItemId(item.id),
                    product_code=ProductCode(item.product_code),
                    feature_code=FeatureCode(item.feature_code),
                    quantity=item.quantity,
                )
                for item in model.items
            ),
        )

    @staticmethod
    def to_model(domain: Subscription) -> SubscriptionModel:
        model = SubscriptionModel(
            subscription_id=str(domain.subscription_id),
            user_id=str(domain.user_id),
            plan_code=str(domain.plan_code),
            status=domain.status.value,
            current_period_start=domain.billing_period.start_at,
            current_period_end=domain.billing_period.end_at,
            cancel_at_period_end=domain.cancel_at_period_end,
            provider_subscription_id=domain.provider_subscription_id,
            last_granted_period_start=domain.last_granted_period_start,
            metadata_json=json.dumps(domain.metadata) if domain.metadata else None,
        )

        model.items = [
            SubscriptionItemModel(
                id=str(item.item_id),
                subscription_id=str(domain.subscription_id),
                product_code=str(item.product_code),
                feature_code=str(item.feature_code),
                quantity=item.quantity,
            )
            for item in domain.items
        ]

        return model

    @staticmethod
    def update_model(
        model: SubscriptionModel,
        domain: Subscription,
    ) -> SubscriptionModel:
        model.user_id = str(domain.user_id)
        model.plan_code = str(domain.plan_code)
        model.status = domain.status.value
        model.current_period_start = domain.billing_period.start_at
        model.current_period_end = domain.billing_period.end_at
        model.cancel_at_period_end = domain.cancel_at_period_end
        model.provider_subscription_id = domain.provider_subscription_id
        model.last_granted_period_start = domain.last_granted_period_start
        model.metadata_json = json.dumps(domain.metadata) if domain.metadata else None

        # Update items using a more efficient approach to minimize database operations
        existing_items_by_id = {item.id: item for item in model.items}
        domain_items_by_id = {str(item.item_id): item for item in domain.items}

        for item_id, domain_item in domain_items_by_id.items():
            existing_item = existing_items_by_id.get(item_id)

            if existing_item is None:
                model.items.append(
                    SubscriptionItemModel(
                        id=item_id,
                        subscription_id=str(domain.subscription_id),
                        product_code=str(domain_item.product_code),
                        feature_code=str(domain_item.feature_code),
                        quantity=domain_item.quantity,
                    )
                )
                continue

            existing_item.product_code = str(domain_item.product_code)
            existing_item.feature_code = str(domain_item.feature_code)
            existing_item.quantity = domain_item.quantity

        for item_id, existing_item in existing_items_by_id.items():
            if item_id not in domain_items_by_id:
                model.items.remove(existing_item)

        return model
