from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from billing.credits.application.commands import (
    ConsumeReservedCreditsCommand,
    CreateCreditAccountCommand,
    ExpireCreditsCommand,
    GrantCreditsCommand,
    PurchaseCreditsCommand,
    ReleaseReservedCreditsCommand,
    ReserveCreditsCommand,
)
from billing.credits.application.exceptions import (
    CreditAccountAlreadyExistsError,
    CreditAccountNotFoundError,
)
from billing.credits.application.handlers import (
    ConsumeReservedCreditsHandler,
    CreateCreditAccountHandler,
    ExpireCreditsHandler,
    GrantCreditsHandler,
    PurchaseCreditsHandler,
    ReleaseReservedCreditsHandler,
    ReserveCreditsHandler,
)
from billing.credits.domain.exceptions import (
    CreditError,
    InsufficientCreditsError,
    InsufficientReservedCreditsError,
    InvalidCreditsAmountError,
)
from billing.credits.interface.dependencies import (
    get_consume_reserved_credits_handler,
    get_create_credit_account_handler,
    get_expire_credits_handler,
    get_grant_credits_handler,
    get_purchase_credits_handler,
    get_release_reserved_credits_handler,
    get_reserve_credits_handler,
)
from billing.credits.interface.mappers import credit_account_response_from_dto
from billing.credits.interface.schemas import (
    ConsumeReservedCreditsRequest,
    CreateCreditAccountRequest,
    CreditAccountResponse,
    ExpireCreditsRequest,
    GrantCreditsRequest,
    PurchaseCreditsRequest,
    ReleaseReservedCreditsRequest,
    ReserveCreditsRequest,
)
from billing.shared.domain.value_objects.user_id import UserId

router = APIRouter(
    prefix="/credits",
    tags=["credits"],
)


@router.post(
    "/accounts",
    response_model=CreditAccountResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_credit_account(
    request: CreateCreditAccountRequest,
    handler: Annotated[
        CreateCreditAccountHandler,
        Depends(get_create_credit_account_handler),
    ],
) -> CreditAccountResponse:
    try:
        dto = await handler.handle(
            CreateCreditAccountCommand(
                user_id=UserId(request.user_id),
            )
        )
    except CreditAccountAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "credit_account_already_exists",
                "message": str(exc),
            },
        ) from exc

    return credit_account_response_from_dto(dto)


@router.post(
    "/grant",
    response_model=CreditAccountResponse,
    status_code=status.HTTP_200_OK,
)
async def grant_credits(
    request: GrantCreditsRequest,
    handler: GrantCreditsHandler = Depends(get_grant_credits_handler),
) -> CreditAccountResponse:
    try:
        dto = await handler.handle(
            GrantCreditsCommand(
                user_id=UserId(request.user_id),
                amount=request.amount,
                source_type=request.source_type,
                source_id=request.source_id,
                description=request.description,
                expires_at=request.expires_at,
            )
        )
    except CreditAccountNotFoundError as exc:
        raise_not_found(exc)
    except CreditError as exc:
        raise_credit_domain_error(exc)

    return credit_account_response_from_dto(dto)


@router.post(
    "/purchase",
    response_model=CreditAccountResponse,
    status_code=status.HTTP_200_OK,
)
async def purchase_credits(
    request: PurchaseCreditsRequest,
    handler: PurchaseCreditsHandler = Depends(get_purchase_credits_handler),
) -> CreditAccountResponse:
    try:
        dto = await handler.handle(
            PurchaseCreditsCommand(
                user_id=UserId(request.user_id),
                amount=request.amount,
                source_id=request.source_id,
                description=request.description,
                expires_at=request.expires_at,
            )
        )
    except CreditAccountNotFoundError as exc:
        raise_not_found(exc)
    except CreditError as exc:
        raise_credit_domain_error(exc)

    return credit_account_response_from_dto(dto)


@router.post(
    "/reserve",
    response_model=CreditAccountResponse,
    status_code=status.HTTP_200_OK,
)
async def reserve_credits(
    request: ReserveCreditsRequest,
    handler: ReserveCreditsHandler = Depends(get_reserve_credits_handler),
) -> CreditAccountResponse:
    try:
        dto = await handler.handle(
            ReserveCreditsCommand(
                user_id=UserId(request.user_id),
                amount=request.amount,
                source_id=request.source_id,
                description=request.description,
            )
        )
    except CreditAccountNotFoundError as exc:
        raise_not_found(exc)
    except CreditError as exc:
        raise_credit_domain_error(exc)

    return credit_account_response_from_dto(dto)


@router.post(
    "/consume-reserved",
    response_model=CreditAccountResponse,
    status_code=status.HTTP_200_OK,
)
async def consume_reserved_credits(
    request: ConsumeReservedCreditsRequest,
    handler: ConsumeReservedCreditsHandler = Depends(
        get_consume_reserved_credits_handler,
    ),
) -> CreditAccountResponse:
    try:
        dto = await handler.handle(
            ConsumeReservedCreditsCommand(
                user_id=UserId(request.user_id),
                amount=request.amount,
                source_id=request.source_id,
                description=request.description,
            )
        )
    except CreditAccountNotFoundError as exc:
        raise_not_found(exc)
    except CreditError as exc:
        raise_credit_domain_error(exc)

    return credit_account_response_from_dto(dto)


@router.post(
    "/release-reserved",
    response_model=CreditAccountResponse,
    status_code=status.HTTP_200_OK,
)
async def release_reserved_credits(
    request: ReleaseReservedCreditsRequest,
    handler: ReleaseReservedCreditsHandler = Depends(
        get_release_reserved_credits_handler,
    ),
) -> CreditAccountResponse:
    try:
        dto = await handler.handle(
            ReleaseReservedCreditsCommand(
                user_id=UserId(request.user_id),
                amount=request.amount,
                source_id=request.source_id,
                description=request.description,
            )
        )
    except CreditAccountNotFoundError as exc:
        raise_not_found(exc)
    except CreditError as exc:
        raise_credit_domain_error(exc)

    return credit_account_response_from_dto(dto)


@router.post(
    "/expire",
    response_model=CreditAccountResponse,
    status_code=status.HTTP_200_OK,
)
async def expire_credits(
    request: ExpireCreditsRequest,
    handler: ExpireCreditsHandler = Depends(get_expire_credits_handler),
) -> CreditAccountResponse:
    try:
        dto = await handler.handle(
            ExpireCreditsCommand(
                user_id=UserId(request.user_id),
                description=request.description,
            )
        )
    except CreditAccountNotFoundError as exc:
        raise_not_found(exc)
    except CreditError as exc:
        raise_credit_domain_error(exc)

    return credit_account_response_from_dto(dto)


# ---------------------------------------------------------------------
# Error mapping
# ---------------------------------------------------------------------


def raise_not_found(exc: Exception) -> None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "code": "credit_account_not_found",
            "message": str(exc),
        },
    ) from exc


def raise_credit_domain_error(exc: CreditError) -> None:
    if isinstance(exc, InvalidCreditsAmountError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        code = "invalid_credits_amount"

    elif isinstance(exc, InsufficientCreditsError):
        status_code = status.HTTP_409_CONFLICT
        code = "insufficient_credits"

    elif isinstance(exc, InsufficientReservedCreditsError):
        status_code = status.HTTP_409_CONFLICT
        code = "insufficient_reserved_credits"

    else:
        status_code = status.HTTP_400_BAD_REQUEST
        code = "credit_operation_failed"

    raise HTTPException(
        status_code=status_code,
        detail={
            "code": code,
            "message": str(exc),
        },
    ) from exc
