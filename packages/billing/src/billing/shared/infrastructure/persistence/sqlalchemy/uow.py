from __future__ import annotations

from db.app_db.session import AppSessionFactory
from sqlalchemy.ext.asyncio import AsyncSession

from billing.shared.application.uow import BillingUoW
from billing.subscription.domain.subscription_repository import SubscriptionRepository
from billing.subscription.infrastructure.persistence.sqlalchemy.repositories.sql_subscription_repository import (
    SQLSubscriptionRepository,
)


class SQLAlchemyBillingUoW(BillingUoW):
    def __init__(
        self,
        session_factory: AppSessionFactory,
    ) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._subscriptions: SubscriptionRepository | None = None

    @property
    def subscriptions(self) -> SubscriptionRepository:
        if self._subscriptions is None:
            raise RuntimeError("UoW has not been entered")

        return self._subscriptions

    async def __aenter__(self) -> SQLAlchemyBillingUoW:
        self._session = self._session_factory()
        self._subscriptions = SQLSubscriptionRepository(self._session)

        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        try:
            await super().__aexit__(exc_type, exc, tb)
        finally:
            if self._session is not None:
                await self._session.close()

    async def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("Session is not initialized")

        await self._session.commit()

    async def rollback(self) -> None:
        if self._session is None:
            raise RuntimeError("Session is not initialized")

        await self._session.rollback()
