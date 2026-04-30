from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from billing.invoice.application.commands import (
    CreateInvoiceCommand,
    CreateInvoiceLineCommand,
    IssueInvoiceCommand,
    MarkInvoicePaidCommand,
    MarkInvoiceUncollectibleCommand,
    VoidInvoiceCommand,
)
from billing.invoice.application.exceptions import InvoiceNotFoundError
from billing.invoice.application.handlers import (
    CreateInvoiceHandler,
    IssueInvoiceHandler,
    MarkInvoicePaidHandler,
    MarkInvoiceUncollectibleHandler,
    VoidInvoiceHandler,
)
from billing.invoice.domain.exceptions import (
    EmptyInvoiceError,
    InvalidInvoiceLineError,
    InvalidInvoiceStateError,
    InvoiceAlreadyPaidError,
)
from billing.invoice.domain.value_objects.invoice_id import InvoiceId
from billing.invoice.interface.dependencies import (
    get_create_invoice_handler,
    get_issue_invoice_handler,
    get_mark_invoice_paid_handler,
    get_mark_invoice_uncollectible_handler,
    get_void_invoice_handler,
)
from billing.invoice.interface.mappers import to_response
from billing.invoice.interface.schemas import (
    CreateInvoiceRequest,
    InvoiceResponse,
)
from billing.shared.domain.value_objects.currency import Currency
from billing.shared.domain.value_objects.money import Money
from billing.shared.domain.value_objects.user_id import UserId

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
)


def map_invoice_error(exc: Exception) -> HTTPException:
    if isinstance(exc, InvoiceNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    if isinstance(
        exc,
        (
            EmptyInvoiceError,
            InvalidInvoiceLineError,
            InvalidInvoiceStateError,
            InvoiceAlreadyPaidError,
        ),
    ):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Unexpected invoice error.",
    )


@router.post(
    "",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_invoice(
    request: CreateInvoiceRequest,
    handler: CreateInvoiceHandler = Depends(get_create_invoice_handler),
) -> InvoiceResponse:
    try:
        dto = await handler.handle(
            CreateInvoiceCommand(
                user_id=UserId(request.user_id),
                lines=tuple(
                    CreateInvoiceLineCommand(
                        description=line.description,
                        quantity=line.quantity,
                        unit_price=Money(
                            amount=line.unit_price_amount,
                            currency=Currency(line.currency),
                        ),
                    )
                    for line in request.lines
                ),
                auto_issue=request.auto_issue,
            )
        )
        return to_response(dto)

    except Exception as exc:
        raise map_invoice_error(exc) from exc


@router.post(
    "/{invoice_id}/issue",
    response_model=InvoiceResponse,
)
async def issue_invoice(
    invoice_id: str,
    handler: IssueInvoiceHandler = Depends(get_issue_invoice_handler),
) -> InvoiceResponse:
    try:
        dto = await handler.handle(
            IssueInvoiceCommand(invoice_id=InvoiceId(invoice_id))
        )
        return to_response(dto)

    except Exception as exc:
        raise map_invoice_error(exc) from exc


@router.post(
    "/{invoice_id}/mark-paid",
    response_model=InvoiceResponse,
)
async def mark_invoice_paid(
    invoice_id: str,
    handler: MarkInvoicePaidHandler = Depends(get_mark_invoice_paid_handler),
) -> InvoiceResponse:
    try:
        dto = await handler.handle(
            MarkInvoicePaidCommand(invoice_id=InvoiceId(invoice_id))
        )
        return to_response(dto)

    except Exception as exc:
        raise map_invoice_error(exc) from exc


@router.post(
    "/{invoice_id}/void",
    response_model=InvoiceResponse,
)
async def void_invoice(
    invoice_id: str,
    handler: VoidInvoiceHandler = Depends(get_void_invoice_handler),
) -> InvoiceResponse:
    try:
        dto = await handler.handle(VoidInvoiceCommand(invoice_id=InvoiceId(invoice_id)))
        return to_response(dto)

    except Exception as exc:
        raise map_invoice_error(exc) from exc


@router.post(
    "/{invoice_id}/mark-uncollectible",
    response_model=InvoiceResponse,
)
async def mark_invoice_uncollectible(
    invoice_id: str,
    handler: MarkInvoiceUncollectibleHandler = Depends(
        get_mark_invoice_uncollectible_handler
    ),
) -> InvoiceResponse:
    try:
        dto = await handler.handle(
            MarkInvoiceUncollectibleCommand(invoice_id=InvoiceId(invoice_id))
        )
        return to_response(dto)

    except Exception as exc:
        raise map_invoice_error(exc) from exc
