from typing import Annotated

from db.app_db.session import AppSessionFactory
from fastapi import Depends, Request

from billing.credits.application.handlers import (
    ExpireCreditsHandler,
    ReleaseReservedCreditsHandler,
)
from billing.invoice.application.handlers import (
    CreateInvoiceHandler,
    IssueInvoiceHandler,
    MarkInvoicePaidHandler,
    MarkInvoiceUncollectibleHandler,
    VoidInvoiceHandler,
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


def get_app_session_factory(request: Request) -> AppSessionFactory:
    return request.app.state.app_session_factory


def get_uow(
    session_factory: Annotated[
        AppSessionFactory,
        Depends(get_app_session_factory),
    ],
) -> BillingUoW:
    return SQLAlchemyBillingUoW(session_factory)


def get_create_invoice_handler(
    uow: Annotated[BillingUoW, Depends(get_uow)],
    clock: Annotated[Clock, Depends(get_clock)],
    id_generator: Annotated[IdGenerator, Depends(get_id_generator)],
    event_publisher: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> CreateInvoiceHandler:
    return CreateInvoiceHandler(
        uow=uow,
        clock=clock,
        id_generator=id_generator,
        event_publisher=event_publisher,
    )


def get_issue_invoice_handler(
    uow: Annotated[BillingUoW, Depends(get_uow)],
    clock: Annotated[Clock, Depends(get_clock)],
    event_publisher: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> IssueInvoiceHandler:
    return IssueInvoiceHandler(
        uow=uow,
        clock=clock,
        event_publisher=event_publisher,
    )


def get_mark_invoice_paid_handler(
    uow: Annotated[BillingUoW, Depends(get_uow)],
    clock: Annotated[Clock, Depends(get_clock)],
    event_publisher: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> MarkInvoicePaidHandler:
    return MarkInvoicePaidHandler(
        uow=uow,
        clock=clock,
        event_publisher=event_publisher,
    )


def get_void_invoice_handler(
    uow: Annotated[BillingUoW, Depends(get_uow)],
    clock: Annotated[Clock, Depends(get_clock)],
    event_publisher: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> VoidInvoiceHandler:
    return VoidInvoiceHandler(
        uow=uow,
        clock=clock,
        event_publisher=event_publisher,
    )


def get_mark_invoice_uncollectible_handler(
    uow: Annotated[BillingUoW, Depends(get_uow)],
    clock: Annotated[Clock, Depends(get_clock)],
    event_publisher: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> MarkInvoiceUncollectibleHandler:
    return MarkInvoiceUncollectibleHandler(
        uow=uow,
        clock=clock,
        event_publisher=event_publisher,
    )


def get_release_reserved_credits_handler(
    uow: Annotated[BillingUoW, Depends(get_uow)],
    clock: Annotated[Clock, Depends(get_clock)],
    event_publisher: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> ReleaseReservedCreditsHandler:
    return ReleaseReservedCreditsHandler(
        uow=uow,
        clock=clock,
        event_publisher=event_publisher,
    )


def get_expire_credits_handler(
    uow: Annotated[BillingUoW, Depends(get_uow)],
    clock: Annotated[Clock, Depends(get_clock)],
    event_publisher: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> ExpireCreditsHandler:
    return ExpireCreditsHandler(
        uow=uow,
        clock=clock,
        event_publisher=event_publisher,
    )
