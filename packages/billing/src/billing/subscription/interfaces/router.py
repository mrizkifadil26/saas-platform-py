from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from billing.shared.application.event_publisher import EventPublisher
from billing.shared.application.id_generator import IdGenerator
from billing.shared.infrastructure.services.system_clock import SystemClock
from billing.shared.infrastructure.services.uuid_generator import UUIDGenerator
from billing.subscription.application.commands import (
    CreateSubscriptionCommand,
    CreateSubscriptionItemCommand,
)
from billing.subscription.application.dto import SubscriptionDTO
from billing.subscription.application.handlers import (
    CreateSubscriptionHandler,
)
from billing.subscription.infrastructure.persistence.sqlalchemy.sql_subscription_uow import (
    SQLSubscriptionUoW,
)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


class CreateSubscriptionItemRequest(BaseModel):
    item_id: str = Field(..., min_length=1)
    product_code: str = Field(..., min_length=1)
    feature_code: str = Field(..., min_length=1)
    quantity: int = Field(default=1, gt=0)


class CreateSubscriptionRequest(BaseModel):
    # TODO: should replace it with customer_id
    user_id: str = Field(..., min_length=1)
    plan_id: str = Field(..., min_length=1)
    period_start: datetime
    period_end: datetime
    items: list[CreateSubscriptionItemRequest] = Field(default_factory=list)
    provider_subscription_id: str | None = None
    trial: bool = False


class SubscriptionItemResponse(BaseModel):
    item_id: str
    product_code: str
    feature_code: str
    quantity: int


class SubscriptionResponse(BaseModel):
    subscription_id: str
    # TODO: should replace it with customer_id
    user_id: str
    plan_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    provider_subscription_id: str | None
    items: list[SubscriptionItemResponse]


def get_session_factory():
    # Replace with config injection later.
    return build_session_factory("sqlite:///./billing.db")


def get_uow(
    session_factory=Depends(get_session_factory),
) -> SQLSubscriptionUoW:
    return SQLSubscriptionUoW(session_factory)


def get_clock() -> SystemClock:
    return SystemClock()


def get_id_generator() -> UUIDGenerator:
    return UUIDGenerator()


class SimpleEventPublisher(EventPublisher):
    def publish(self, events) -> None:
        # Replace with outbox/event bus later.
        for _event in events:
            pass


def get_event_publisher() -> EventPublisher:
    return SimpleEventPublisher()


def to_response(dto: SubscriptionDTO) -> SubscriptionResponse:
    return SubscriptionResponse(
        subscription_id=dto.subscription_id,
        # TODO: should replace it with customer_id
        user_id=dto.user_id,
        plan_id=dto.plan_id,
        status=dto.status,
        current_period_start=dto.current_period_start,
        current_period_end=dto.current_period_end,
        cancel_at_period_end=dto.cancel_at_period_end,
        provider_subscription_id=dto.provider_subscription_id,
        items=[
            SubscriptionItemResponse(
                item_id=item.item_id,
                product_code=item.product_code,
                feature_code=item.feature_code,
                quantity=item.quantity,
            )
            for item in dto.items
        ],
    )


@router.post(
    "",
    response_model=SubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_subscription(
    request: CreateSubscriptionRequest,
    # uow=Depends(get_subscription_uow),
    uow: Annotated[SQLSubscriptionUoW, Depends(get_uow)],
    clock: Annotated[SystemClock, Depends(get_clock)],
    id_generator: Annotated[IdGenerator, Depends(get_id_generator)],
    event_publisher: Annotated[EventPublisher, Depends(get_event_publisher)],
):
    # service = SubscriptionApplicationService(uow)
    handler = CreateSubscriptionHandler(
        uow=uow,
        id_generator=id_generator,
        clock=clock,
        event_publisher=event_publisher,
    )

    # result = await service.create_subscription(
    #     CreateSubscriptionCommand(
    #         user_id=payload["user_id"],
    #         plan_code=payload["plan_code"],
    #         current_period_start=payload["current_period_start"],
    #         current_period_end=payload["current_period_end"],
    #         provider_subscription_id=payload.get("provider_subscription_id"),
    #     )
    # )
    dto = handler.handle(
        CreateSubscriptionCommand(
            # TODO: should replace it with customer_id
            user_id=request.user_id,
            plan_id=request.plan_id,
            period_start=request.period_start,
            period_end=request.period_end,
            items=tuple(
                CreateSubscriptionItemCommand(
                    item_id=item.item_id,
                    product_code=item.product_code,
                    feature_code=item.feature_code,
                    quantity=item.quantity,
                )
                for item in request.items
            ),
            provider_subscription_id=request.provider_subscription_id,
            trial=request.trial,
        )
    )

    return to_response(dto)
