from typing import Annotated

from db.app_db.session import (
    AppSessionFactory,
    get_app_session_factory,
)
from fastapi import Depends

from billing.payg.application.handlers import (
    GrantPaygCreditsHandler,
    PurchasePaygCreditsHandler,
)
from billing.payment.domain.payment_gateway import PaymentGateway
from billing.payment.infrastructure.gateways.fake_payment_gateway import (
    FakePaymentGateway,
)
from billing.pricing.application.catalogs import PaygPricingCatalog
from billing.pricing.infrastructure.catalogs.static_payg_catalog import (
    StaticPaygCatalog,
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


def get_uow(
    session_factory: Annotated[
        AppSessionFactory,
        Depends(get_app_session_factory),
    ],
) -> BillingUoW:
    return SQLAlchemyBillingUoW(session_factory)


def get_pricing_catalog() -> PaygPricingCatalog:
    return StaticPaygCatalog()


def get_payment_gateway() -> PaymentGateway:
    return FakePaymentGateway()  # Replace with actual implementation


def get_purchase_payg_credits_handler(
    uow: Annotated[BillingUoW, Depends(get_uow)],
    id_generator: Annotated[IdGenerator, Depends(get_id_generator)],
    pricing_catalog: Annotated[PaygPricingCatalog, Depends(get_pricing_catalog)],
    payment_gateway: Annotated[PaymentGateway, Depends(get_payment_gateway)],
    clock: Annotated[Clock, Depends(get_clock)],
    event_publisher: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> PurchasePaygCreditsHandler:
    return PurchasePaygCreditsHandler(
        uow=uow,
        id_generator=id_generator,
        pricing_catalog=pricing_catalog,
        payment_gateway=payment_gateway,
        clock=clock,
        event_publisher=event_publisher,
    )


def get_grant_payg_credits_handler(
    uow: Annotated[BillingUoW, Depends(get_uow)],
    id_generator: Annotated[IdGenerator, Depends(get_id_generator)],
    clock: Annotated[Clock, Depends(get_clock)],
    event_publisher: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> GrantPaygCreditsHandler:
    return GrantPaygCreditsHandler(
        uow=uow,
        clock=clock,
        id_generator=id_generator,
        event_publisher=event_publisher,
    )
