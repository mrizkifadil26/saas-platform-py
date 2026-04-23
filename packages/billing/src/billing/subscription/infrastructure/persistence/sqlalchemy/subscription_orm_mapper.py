import json

from billing.shared.domain.value_objects.user_id import UserId
from billing.subscription.domain.subscription import Subscription
from billing.subscription.domain.subscription_status import SubscriptionStatus
from billing.subscription.domain.value_objects.billing_period import BillingPeriod
from billing.subscription.domain.value_objects.plan_id import PlanId
from billing.subscription.domain.value_objects.subscription_id import SubscriptionId
from billing.subscription.infrastructure.persistence.sqlalchemy.subscription_item_model import (
    SubscriptionItemModel,
)
from billing.subscription.infrastructure.persistence.sqlalchemy.subscription_model import (
    SubscriptionModel,
)


class SubscriptionORMMapper:
    @staticmethod
    def to_domain(model: SubscriptionModel) -> Subscription:
        # raw_user_id = model.user_id
        # try:
        #     user_id_value = UUID(raw_user_id)
        # except ValueError:
        #     user_id_value = raw_user_id

        # if model.status not in (
        #     "active",
        #     "canceled",
        #     "past_due",
        # ):
        #     raise ValueError(f"Invalid subscription status persisted in DB: {model.status}")

        # status = cast(SubscriptionStatus, model.status)

        return Subscription(
            subscription_id=SubscriptionId(model.subscription_id),
            user_id=UserId(model.user_id),
            plan_id=PlanId(model.plan_id),
            status=SubscriptionStatus(model.status),
            billing_period=BillingPeriod(
                start_at=model.current_period_start,
                end_at=model.current_period_end,
            ),
            cancel_at_period_end=model.cancel_at_period_end,
            provider_subscription_id=model.provider_subscription_id,
            last_granted_period_start=model.last_granted_period_start,
            metadata=json.loads(model.metadata_json) if model.metadata_json else {},
        )

    @staticmethod
    def to_model(domain: Subscription) -> SubscriptionModel:
        model = SubscriptionModel(
            subscription_id=domain.subscription_id,
            # TODO: should use customer_id than user_id
            user_id=domain.user_id,
            plan_id=domain.plan_id,
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
                id=item.item_id,
                subscription_id=domain.subscription_id,
                product_code=item.product_code,
                feature_code=item.feature_code,
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
        # TODO: should use customer_id than user_id
        model.user_id = str(domain.user_id)
        model.plan_id = str(domain.plan_id)
        model.status = domain.status.value
        model.current_period_start = domain.billing_period.start_at
        model.current_period_end = domain.billing_period.end_at
        model.cancel_at_period_end = domain.cancel_at_period_end
        model.provider_subscription_id = domain.provider_subscription_id
        model.last_granted_period_start = domain.last_granted_period_start
        model.metadata_json = json.dumps(domain.metadata) if domain.metadata else None

        model.items.clear()
        model.items.extend(
            [
                SubscriptionItemModel(
                    id=item.item_id,
                    subscription_id=domain.subscription_id,
                    product_code=item.product_code,
                    feature_code=item.feature_code,
                    quantity=item.quantity,
                )
                for item in domain.items
            ]
        )
        return model


# def copy_to_model(
#     subscription: Subscription,
#     model: SubscriptionModel,
# ) -> SubscriptionModel:
#     model.subscription_id = str(subscription.subscription_id)
#     model.user_id = str(subscription.user_id)
#     model.plan_code = str(subscription.plan_code)
#     model.status = subscription.status
#     model.current_period_start = subscription.current_period_start
#     model.current_period_end = subscription.current_period_end
#     model.cancel_at_period_end = subscription.cancel_at_period_end
#     model.provider_subscription_id = subscription.provider_subscription_id
#     model.last_granted_period_start = subscription.last_granted_period_start

#     return model
