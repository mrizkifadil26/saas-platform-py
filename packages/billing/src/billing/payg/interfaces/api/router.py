from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from billing.payg.application.commands import PurchasePaygCreditsCommand
from billing.payg.application.exceptions import PaygPurchaseNotFoundError
from billing.payg.application.handlers import PurchasePaygCreditsHandler
from billing.payg.domain.value_objects.pack_code import PackCode
from billing.payg.interfaces.api.dependencies import get_purchase_payg_credits_handler
from billing.payg.interfaces.api.schemas import (
    PaygPurchaseResponse,
    PurchasePaygCreditsRequest,
)
from billing.payment.domain.value_objects.payment_method import PaymentMethod
from billing.shared.domain.value_objects.user_id import UserId

router = APIRouter(
    prefix="/payg",
    tags=["payg"],
)


@router.post(
    "",
    response_model=PaygPurchaseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def purchase_payg_credits(
    request: PurchasePaygCreditsRequest,
    handler: Annotated[
        PurchasePaygCreditsHandler,
        Depends(get_purchase_payg_credits_handler),
    ],
) -> PaygPurchaseResponse:
    command = PurchasePaygCreditsCommand(
        user_id=UserId(request.customer_id),
        # plan_id=request.plan_id,
        pack_code=PackCode(request.package_code),
        payment_method=PaymentMethod(
            type=request.payment_method,
            provider=request.payment_provider,
            reference=request.payment_reference,
        ),
        idempotency_key=request.idempotency_key,
    )
    result = await handler.handle(command)

    return PaygPurchaseResponse(
        purchase_id=result.purchase.id,
        user_id=result.purchase.user_id,
        credits=result.purchase.credits,
        status=result.purchase.status,
    )


# @router.get("/purchases/{purchase_id}", response_model=PaygPurchaseResponse)
# async def get_purchase(
#     purchase_id: str,
#     handler: Annotated[
#         ...,
#         ...,
#     ],
# ) -> PaygPurchaseResponse:
#     try:
#         result = await handler.get_purchase(purchase_id)  # assume you expose this
#     except PaygPurchaseNotFoundError as e:
#         raise HTTPException(status_code=404, detail=str(e))

#     return PaygPurchaseResponse(
#         purchase_id=result.purchase_id,
#         user_id=result.user_id,
#         credits=result.credits,
#         status=result.status,
#     )


# @router.get("/packs", response_model=...)
# async def get_payg_packs(
#     handler: Annotated[
#         ...,
#         ...,
#     ],
# ) -> PaygPurchaseResponse:
#     try:
#         result = await handler.get_purchase(purchase_id)  # assume you expose this
#     except PaygPurchaseNotFoundError as e:
#         raise HTTPException(status_code=404, detail=str(e))

#     return PaygPurchaseResponse(
#         purchase_id=result.purchase_id,
#         user_id=result.user_id,
#         credits=result.credits,
#         status=result.status,
#     )
