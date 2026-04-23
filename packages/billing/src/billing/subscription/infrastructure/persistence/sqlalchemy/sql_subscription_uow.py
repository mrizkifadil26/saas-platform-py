from __future__ import annotations

from billing.subscription.application.uow import SubscriptionUnitOfWork
from billing.subscription.infrastructure.persistence.sqlalchemy.repositories.sql_subscription_repository import (
    SQLSubscriptionRepository,
)
from sqlalchemy.orm import Session, sessionmaker


class SQLSubscriptionUoW(SubscriptionUnitOfWork):
    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self.subscriptions: SQLSubscriptionRepository

    def __enter__(self) -> SQLSubscriptionUoW:
        self._session = self._session_factory()
        self.subscriptions = SQLSubscriptionRepository(
            self._session,
        )

        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._session is None:
            return

        if exc_type:
            self.rollback()

        self._session.close()

    def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("UnitOfWork session is not initialized")

        self._session.commit()

    def rollback(self) -> None:
        if self._session is None:
            raise RuntimeError("UnitOfWork session is not initialized")

        self._session.rollback()
