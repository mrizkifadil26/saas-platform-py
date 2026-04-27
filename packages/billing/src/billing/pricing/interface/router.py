from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from billing.pricing.application.handlers import (
    CreatePricingSnapshotHandler,
    GetPricingRuleHandler,
)
from billing.pricing.application.queries import (
    CreatePricingSnapshotQuery,
    GetPricingRuleQuery,
)
from billing.pricing.exceptions import PricingRuleNotFound
from billing.pricing.interface.dependencies import (
    get_create_pricing_snapshot_handler,
    get_pricing_rule_handler,
)
from billing.pricing.interface.schemas import (
    PricingRuleResponse,
    PricingSnapshotResponse,
)

router = APIRouter(
    prefix="/pricing",
    tags=["pricing"],
)


@router.get(
    "/rules/{pricing_key}",
    response_model=PricingRuleResponse,
)
async def get_pricing_rule(
    pricing_key: str,
    at: datetime,
    handler: GetPricingRuleHandler = Depends(get_pricing_rule_handler),
) -> PricingRuleResponse:
    try:
        dto = await handler.handle(
            GetPricingRuleQuery(
                pricing_key=pricing_key,
                at=at,
            )
        )
    except PricingRuleNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return PricingRuleResponse(
        id=dto.id,
        pricing_key=dto.pricing_key,
        amount=dto.amount,
        currency=dto.currency,
        billing_scheme=dto.billing_scheme,
        active_from=dto.active_from,
        active_until=dto.active_until,
    )


@router.post(
    "/snapshots/{pricing_key}",
    response_model=PricingSnapshotResponse,
)
async def create_pricing_snapshot(
    pricing_key: str,
    at: datetime,
    handler: CreatePricingSnapshotHandler = Depends(
        get_create_pricing_snapshot_handler
    ),
) -> PricingSnapshotResponse:
    try:
        dto = await handler.handle(
            CreatePricingSnapshotQuery(
                pricing_key=pricing_key,
                at=at,
            )
        )
    except PricingRuleNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return PricingSnapshotResponse(
        pricing_rule_id=dto.pricing_rule_id,
        pricing_key=dto.pricing_key,
        unit_amount=dto.unit_amount,
        currency=dto.currency,
        billing_scheme=dto.billing_scheme,
        captured_at=dto.captured_at,
    )
