from billing.credits.application.dto import (
    CreditAccountDTO,
    CreditBalanceDTO,
    CreditGrantDTO,
    CreditLedgerEntryDTO,
)
from billing.credits.interface.schemas import (
    CreditAccountResponse,
    CreditBalanceResponse,
    CreditGrantResponse,
    CreditLedgerEntryResponse,
)


def credit_account_response_from_dto(dto: CreditAccountDTO) -> CreditAccountResponse:
    return CreditAccountResponse(
        id=str(dto.id),
        user_id=str(dto.user_id),
        balance=credit_balance_response_from_dto(dto.balance),
        grants=[credit_grant_response_from_dto(grant) for grant in dto.grants],
        ledger_entries=[
            credit_ledger_entry_response_from_dto(entry) for entry in dto.ledger_entries
        ],
    )


def credit_balance_response_from_dto(dto: CreditBalanceDTO) -> CreditBalanceResponse:
    return CreditBalanceResponse(
        available=dto.available,
        reserved=dto.reserved,
        total=dto.total,
    )


def credit_grant_response_from_dto(dto: CreditGrantDTO) -> CreditGrantResponse:
    return CreditGrantResponse(
        id=str(dto.id),
        credit_account_id=str(dto.credit_account_id),
        amount=dto.amount,
        remaining=dto.remaining,
        granted_at=dto.granted_at,
        expires_at=dto.expires_at,
        source_id=dto.source_id,
    )


def credit_ledger_entry_response_from_dto(
    dto: CreditLedgerEntryDTO,
) -> CreditLedgerEntryResponse:
    return CreditLedgerEntryResponse(
        id=str(dto.id),
        credit_account_id=str(dto.credit_account_id),
        amount=dto.amount,
        balance_after_available=dto.balance_after_available,
        balance_after_reserved=dto.balance_after_reserved,
        source_type=dto.source_type,
        source_id=dto.source_id,
        description=dto.description,
        occurred_at=dto.occurred_at,
    )
