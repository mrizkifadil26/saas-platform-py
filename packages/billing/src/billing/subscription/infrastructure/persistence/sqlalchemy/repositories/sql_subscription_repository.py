from db.repositories.app.base import AsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from billing.shared.domain.value_objects.user_id import UserId
from billing.subscription.domain.subscription import Subscription
from billing.subscription.domain.subscription_repository import SubscriptionRepository
from billing.subscription.infrastructure.persistence.sqlalchemy.mappers.subscription_orm_mapper import (
    SubscriptionORMMapper,
)

from ..models.subscription_model import (
    SubscriptionModel,
)


class SQLSubscriptionRepository(
    AsyncRepository,
    SubscriptionRepository,
):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        # self._session = session

    def get(
        self,
        subscription_id: str,
    ) -> Subscription | None:
        model = self.db.get(
            SubscriptionModel,
            # str(subscription_id),
            subscription_id,
        )
        if model is None:
            return None

        return SubscriptionORMMapper.to_domain(model)

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

        return SubscriptionORMMapper.to_domain(model)

    def save(self, subscription: Subscription) -> None:
        existing = self.db.get(
            SubscriptionModel,
            str(subscription.subscription_id),
        )

        if existing is None:
            model = SubscriptionORMMapper.to_model(subscription)
            # model = SubscriptionModel(
            #     subscription_id=str(subscription.subscription_id),
            # )
            self.db.add(model)
            return

        SubscriptionORMMapper.update_model(existing, subscription)


def delete(self, subscription: Subscription) -> None:
    existing = self._session.get(SubscriptionModel, subscription.subscription_id)
    if existing is not None:
        self._session.delete(existing)
