from db.uow.base import AsyncUnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession

from billing.subscription.application.interfaces import (
    CreditGrantWriter,
    SubscriptionApplicationUnitOfWork,
)
from billing.subscription.domain.subscription_repository import SubscriptionRepository
from billing.subscription.infrastructure.repositories import (
    SqlAlchemySubscriptionRepository,
)


class SubscriptionUnitOfWork(AsyncUnitOfWork, SubscriptionApplicationUnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.subscriptions = SqlAlchemySubscriptionRepository(session)

    subscription: SubscriptionRepository
    credit_grant: CreditGrantWriter

    async def commit(self) -> None:
        raise NotImplementedError

    async def rollback(self) -> None:
        raise NotImplementedError
