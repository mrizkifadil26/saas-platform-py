from typing import Annotated

from db.app_db.session import AppSessionFactory
from fastapi import Depends, Request

from billing.credits.application.handlers import (
    ConsumeReservedCreditsHandler,
    CreateCreditAccountHandler,
    ExpireCreditsHandler,
    GrantCreditsHandler,
    ReleaseReservedCreditsHandler,
    ReserveCreditsHandler,
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


def get_create_credit_account_handler(
    uow: Annotated[BillingUoW, Depends(get_uow)],
    id_generator: Annotated[IdGenerator, Depends(get_id_generator)],
    event_publisher: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> CreateCreditAccountHandler:
    return CreateCreditAccountHandler(
        uow=uow,
        id_generator=id_generator,
        event_publisher=event_publisher,
    )


def get_grant_credits_handler(
    uow: Annotated[BillingUoW, Depends(get_uow)],
    id_generator: Annotated[IdGenerator, Depends(get_id_generator)],
    clock: Annotated[Clock, Depends(get_clock)],
    event_publisher: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> GrantCreditsHandler:
    return GrantCreditsHandler(
        uow=uow,
        id_generator=id_generator,
        clock=clock,
        event_publisher=event_publisher,
    )


def get_reserve_credits_handler(
    uow: Annotated[BillingUoW, Depends(get_uow)],
    clock: Annotated[Clock, Depends(get_clock)],
    event_publisher: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> ReserveCreditsHandler:
    return ReserveCreditsHandler(
        uow=uow,
        clock=clock,
        event_publisher=event_publisher,
    )


def get_consume_reserved_credits_handler(
    uow: Annotated[BillingUoW, Depends(get_uow)],
    clock: Annotated[Clock, Depends(get_clock)],
    event_publisher: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> ConsumeReservedCreditsHandler:
    return ConsumeReservedCreditsHandler(
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
