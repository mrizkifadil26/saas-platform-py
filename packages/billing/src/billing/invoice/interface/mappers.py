from billing.invoice.interface.schemas import InvoiceLineResponse, InvoiceResponse


def to_response(dto) -> InvoiceResponse:
    return InvoiceResponse(
        id=dto.id,
        user_id=dto.user_id,
        status=dto.status,
        total_amount=dto.total_amount,
        currency=dto.currency,
        lines=[
            InvoiceLineResponse(
                description=line.description,
                quantity=line.quantity,
                unit_price_amount=line.unit_price_amount,
                currency=line.currency,
                total_amount=line.total_amount,
            )
            for line in dto.lines
        ],
        created_at=dto.created_at,
        issued_at=dto.issued_at,
        paid_at=dto.paid_at,
        voided_at=dto.voided_at,
        uncollectible_at=dto.uncollectible_at,
    )
