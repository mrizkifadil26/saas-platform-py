from fastapi import APIRouter, Depends

from billing.subscription.application.commands import CreateSubscriptionCommand
from billing.subscription.application.services import SubscriptionApplicationService
from billing.subscription.infrastructure.dependencies import get_subscription_uow

router = APIRouter()


@router.post("/subscriptions")
async def create_subscription(
    payload: dict,
    uow=Depends(get_subscription_uow),
):
    service = SubscriptionApplicationService(uow)
    result = await service.create_subscription(
        CreateSubscriptionCommand(
            user_id=payload["user_id"],
            plan_code=payload["plan_code"],
            current_period_start=payload["current_period_start"],
            current_period_end=payload["current_period_end"],
            provider_subscription_id=payload.get("provider_subscription_id"),
        )
    )

    return result
