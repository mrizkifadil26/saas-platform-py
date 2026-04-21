from sqlalchemy.ext.asyncio import AsyncSession

from billing.application.subscription.interfaces import (
    CreditGrantWriter,
    SubscriptionApplicationUnitOfWork,
)
from billing.domain.subscription.repositories import (
    SubscriptionRepository,
)
from billing.infrastructure.subscription.repositories import (
    SqlAlchemySubscriptionRepository,
)

from db.uow.base import AsyncUnitOfWork


class SubscriptionUnitOfWork(
    AsyncUnitOfWork, SubscriptionApplicationUnitOfWork
):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.subscriptions = (
            SqlAlchemySubscriptionRepository(session)
        )

    subscription: SubscriptionRepository
    credit_grant: CreditGrantWriter

    async def commit(self) -> None:
        raise NotImplementedError

    async def rollback(self) -> None:
        raise NotImplementedError
