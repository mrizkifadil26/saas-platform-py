from packages.db.src.db.session import SessionLocal

from billing.application.subscription.interfaces import (
    SubscriptionApplicationUnitOfWork,
)
from billing.infrastructure.subscription.repositories import (
    SqlAlchemySubscriptionRepository,
)


class SubscriptionUnitOfWork(
    SqlAlchemyUnitOfWork, SubscriptionApplicationUnitOfWork
):
    def __init__(self, session: SessionLocal) -> None:
        super().__init__(session)
        self.subscriptions = (
            SqlAlchemySubscriptionRepository(session)
        )
