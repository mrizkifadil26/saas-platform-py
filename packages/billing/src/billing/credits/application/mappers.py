from billing.credits.application.dto import (
    CreditAccountDTO,
    CreditBalanceDTO,
    CreditGrantDTO,
    CreditLedgerEntryDTO,
)
from billing.credits.domain.credit_account import CreditAccount
from billing.credits.domain.credit_grant import CreditGrant
from billing.credits.domain.credit_ledger_entry import CreditLedgerEntry


class CreditAccountMapper:
    @staticmethod
    def to_dto(account: CreditAccount) -> CreditAccountDTO:
        return CreditAccountDTO(
            id=account.id,
            user_id=account.user_id,
            balance=CreditAccountMapper._map_balance(account),
            grants=tuple(
                CreditAccountMapper._map_grant(grant) for grant in account.grants
            ),
            ledger_entries=tuple(
                CreditAccountMapper._map_ledger_entry(entry)
                for entry in account.ledger_entries
            ),
        )

    @staticmethod
    def _map_balance(account: CreditAccount) -> CreditBalanceDTO:
        return CreditBalanceDTO(
            available=int(account.balance.available),
            reserved=int(account.balance.reserved),
            total=int(account.balance.total),
        )

    @staticmethod
    def _map_grant(grant: CreditGrant) -> CreditGrantDTO:
        return CreditGrantDTO(
            id=grant.id,
            credit_account_id=grant.credit_account_id,
            amount=int(grant.amount),
            remaining=int(grant.remaining),
            granted_at=grant.granted_at,
            expires_at=grant.expires_at,
            source_id=grant.source_id,
        )

    @staticmethod
    def _map_ledger_entry(entry: CreditLedgerEntry) -> CreditLedgerEntryDTO:
        return CreditLedgerEntryDTO(
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
