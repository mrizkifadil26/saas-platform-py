from typing import Annotated

from db.app_db.session import AppSessionFactory
from fastapi import Depends, Request

from billing.pricing.application.catalogs import SubscriptionPricingCatalog
from billing.pricing.infrastructure.catalogs.static_subscription_catalog import (
    StaticSubscriptionCatalog,
)
from billing.shared.application.clock import Clock
from billing.shared.application.event_publisher import EventPublisher
from billing.shared.application.id_generator import IdGenerator
from billing.shared.application.uow import BillingUoW
from billing.shared.infrastructure.persistence.sqlalchemy.uow import (
    SQLAlchemyBillingUoW,
)
from billing.shared.infrastructure.services.system_clock import SystemClock
from billing.shared.infrastructure.services.uuid_generator import UUIDGenerator
from billing.subscription.application.handlers import CreateSubscriptionHandler


class SimpleEventPublisher(EventPublisher):
    def publish(self, events) -> None:
        # Replace with outbox/event bus later.
        for _event in events:
            pass


def get_clock() -> SystemClock:
    return SystemClock()


def get_id_generator() -> UUIDGenerator:
    return UUIDGenerator()


def get_event_publisher() -> EventPublisher:
    return SimpleEventPublisher()


def get_app_session_factory(request: Request) -> AppSessionFactory:
    return request.app.state.app_session_factory


def get_uow(
    session_factory: Annotated[
        AppSessionFactory,
        Depends(get_app_session_factory),
    ],
) -> BillingUoW:
    return SQLAlchemyBillingUoW(session_factory)


def get_pricing_catalog() -> SubscriptionPricingCatalog:
    return StaticSubscriptionCatalog()


def get_create_subscription_handler(
    uow: Annotated[BillingUoW, Depends(get_uow)],
    id_generator: Annotated[IdGenerator, Depends(get_id_generator)],
    pricing_catalog: Annotated[
        SubscriptionPricingCatalog, Depends(get_pricing_catalog)
    ],
    clock: Annotated[Clock, Depends(get_clock)],
    event_publisher: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> CreateSubscriptionHandler:
    return CreateSubscriptionHandler(
        uow=uow,
        id_generator=id_generator,
        pricing_catalog=pricing_catalog,
        clock=clock,
        event_publisher=event_publisher,
    )
