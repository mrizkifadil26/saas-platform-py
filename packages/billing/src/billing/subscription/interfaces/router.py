from typing import Annotated

from fastapi import APIRouter, Depends, status

from billing.subscription.application.commands import (
    CreateSubscriptionCommand,
    CreateSubscriptionItemCommand,
)
from billing.subscription.application.handlers import (
    CreateSubscriptionHandler,
)
from billing.subscription.interfaces.dependencies import get_create_subscription_handler
from billing.subscription.interfaces.mappers import to_response
from billing.subscription.interfaces.schemas import (
    CreateSubscriptionRequest,
    SubscriptionResponse,
)

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
)


@router.post(
    "",
    response_model=SubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_subscription(
    request: CreateSubscriptionRequest,
    handler: Annotated[
        CreateSubscriptionHandler,
        Depends(get_create_subscription_handler),
    ],
) -> SubscriptionResponse:
    dto = await handler.handle(
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
