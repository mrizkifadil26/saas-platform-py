from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class PaygPurchaseDTO:
    purchase_id: str
    user_id: str
    plan_code: str
    credits: int
    created_at: datetime
    request_id: str | None
    metadata: dict[str, str]


@dataclass(frozen=True, slots=True)
class PaygPurchaseResultDTO:
    purchase: PaygPurchaseDTO
    grant_id: str
    granted_credits: int
    expires_at: datetime | None
    price_cents: int
    currency: str


def to_payg_purchase_dto(purchase) -> PaygPurchaseDTO:
    return PaygPurchaseDTO(
        purchase_id=str(purchase.purchase_id),
        user_id=str(purchase.user_id),
        plan_code=str(purchase.plan_code),
        credits=int(purchase.credits),
        created_at=purchase.created_at,
        request_id=str(purchase.request_id)
        if purchase.request_id is not None
        else None,
        metadata=dict(purchase.metadata),
    )


def to_payg_purchase_result_dto(
    result,
) -> PaygPurchaseResultDTO:
    return PaygPurchaseResultDTO(
        purchase=to_payg_purchase_dto(result.purchase),
        grant_id=str(result.grant.grant_id),
        granted_credits=int(result.grant.granted_credits),
        expires_at=result.grant.expires_at,
        price_cents=result.pack.price_cents,
        currency=result.pack.currency,
    )
