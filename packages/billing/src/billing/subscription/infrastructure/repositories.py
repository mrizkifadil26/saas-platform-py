from db.repositories.app.base import AsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from billing.shared.domain.value_objects.user_id import UserId
from billing.subscription.domain.subscription import Subscription
from billing.subscription.domain.subscription_repository import SubscriptionRepository
from billing.subscription.domain.value_objects.subscription_id import SubscriptionId
from billing.subscription.infrastructure.mappers import copy_to_model, to_domain

from .models import (
    SubscriptionModel,
)


class SqlAlchemySubscriptionRepository(
    AsyncRepository,
    SubscriptionRepository,
):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def get(
        self,
        subscription_id: SubscriptionId,
    ) -> Subscription | None:
        model = self.db.get(
            SubscriptionModel,
            str(subscription_id),
        )
        if not model:
            return None

        return to_domain(model)

    def get_active_for_user(self, user_id: UserId) -> Subscription | None:
        model = (
            self.db.query(SubscriptionModel)
            .filter_by(
                user_id=str(user_id),
                status="active",
            )
            .order_by(SubscriptionModel.current_period_end.desc())
            .first()
        )

        if model is None:
            return None

        return to_domain(model)

    def save(self, subscription: Subscription) -> None:
        model = self.db.get(
            SubscriptionModel,
            str(subscription.subscription_id),
        )

        if model is None:
            model = SubscriptionModel(
                subscription_id=str(subscription.subscription_id),
            )
            self.db.add(model)

        copy_to_model(subscription, model)
