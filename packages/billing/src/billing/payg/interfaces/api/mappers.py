from billing.payg.application.dto import PaygPurchaseDTO
from billing.payg.interfaces.api.schemas import PaygPurchaseResponse


def to_response(dto: PaygPurchaseDTO) -> PaygPurchaseResponse:
    return PaygPurchaseResponse(
        purchase_id=dto.id,
        # TODO: should replace it with customer_id
        user_id=dto.user_id,
        credits=dto.credits,
        status=dto.status,
    )
