from billing.credits.application.dto import (
    CreditAccountDTO,
    CreditBalanceDTO,
    CreditGrantDTO,
    CreditLedgerEntryDTO,
)
from billing.credits.domain.credit_account import CreditAccount


class CreditAccountMapper:
    @staticmethod
    def domain_to_dto(account: CreditAccount) -> CreditAccountDTO:
        return CreditAccountDTO(
            id=account.id,
            # TODO: should use customer_id instead of user_id
            user_id=account.user_id,
            balance=CreditBalanceDTO(
                available=int(account.balance.available),
                reserved=int(account.balance.reserved),
                total=int(account.balance.total),
            ),
            grants=tuple(
                CreditGrantDTO(
                    id=grant.id,
                    credit_account_id=grant.credit_account_id,
                    amount=int(grant.amount),
                    remaining=int(grant.remaining),
                    granted_at=grant.granted_at,
                    expires_at=grant.expires_at,
                    source_id=grant.source_id,
                )
                for grant in account.grants
            ),
            ledger_entries=tuple(
                CreditLedgerEntryDTO(
                    id=entry.id,
                    credit_account_id=entry.credit_account_id,
                    delta=entry.delta,
                    balance_after_available=int(entry.balance_after_available),
                    balance_after_reserved=int(entry.balance_after_reserved),
                    source_type=entry.source_type,
                    source_id=entry.source_id,
                    description=entry.description,
                    occurred_at=entry.occurred_at,
                )
                for entry in account.ledger_entries
            ),
        )
