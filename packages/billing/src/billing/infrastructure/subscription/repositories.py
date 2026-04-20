from packages.db.src.db.session import SessionLocal

from billing.domain.shared.ids import UserId
from billing.domain.subscription.entities import (
    Subscription,
)
from billing.domain.subscription.repositories import (
    SubscriptionRepository,
)
from billing.domain.subscription.value_objects import (
    SubscriptionId,
)
from billing.infrastructure.subscription.mappers import (
    copy_to_model,
    to_domain,
)

from .models import (
    SubscriptionModel,
)


class SqlAlchemySubscriptionRepository(
    SubscriptionRepository
):
    def __init__(self, session: SessionLocal) -> None:
        super().__init__(session)

    def get(
        self, subscription_id: SubscriptionId
    ) -> Subscription | None:
        model = self.session.get(
            SubscriptionModel, str(subscription_id)
        )
        if not model:
            return None

        return to_domain(model)

    def get_active_for_user(
        self, user_id: UserId
    ) -> Subscription | None:
        model = (
            self.session.query(SubscriptionModel)
            .filter_by(
                user_id=str(user_id),
                status="active",
            )
            .order_by(
                SubscriptionModel.current_period_end.desc()
            )
            .first()
        )

        if model is None:
            return None

        return to_domain(model)

    def save(self, subscription: Subscription) -> None:
        model = self.session.get(
            SubscriptionModel,
            str(subscription.subscription_id),
        )

        if model is None:
            model = SubscriptionModel(
                subscription_id=str(
                    subscription.subscription_id
                ),
            )
            self.session.add(model)

        copy_to_model(subscription, model)
