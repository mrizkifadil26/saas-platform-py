from billing.credits.domain.credit_account import CreditAccount
from billing.credits.domain.credit_balance import CreditBalance
from billing.credits.domain.credit_grant import CreditGrant
from billing.credits.domain.credit_ledger_entry import CreditLedgerEntry
from billing.credits.domain.credit_source_type import CreditSourceType
from billing.credits.domain.value_objects.credit_account_id import CreditAccountId
from billing.credits.domain.value_objects.credit_grant_id import CreditGrantId
from billing.credits.domain.value_objects.credit_ledger_entry_id import (
    CreditLedgerEntryId,
)
from billing.credits.domain.value_objects.credits import Credits
from billing.credits.infrastructure.persistence.sqlalchemy.models import (
    CreditAccountModel,
    CreditGrantModel,
    CreditLedgerEntryModel,
)
from billing.shared.domain.value_objects.user_id import UserId


class CreditAccountORMMapper:
    @staticmethod
    def from_model(model: CreditAccountModel) -> CreditAccount:
        return CreditAccount(
            id=CreditAccountId(model.id),
            user_id=UserId(model.user_id),
            balance=CreditBalance(
                available=Credits.of(model.available_balance),
                reserved=Credits.of(model.reserved_balance),
            ),
            grants=[
                CreditGrantORMMapper.from_model(grant_model)
                for grant_model in model.grants
            ],
            ledger_entries=[
                CreditLedgerEntryORMMapper.from_model(entry_model)
                for entry_model in model.ledger_entries
            ],
        )

    @staticmethod
    def to_model(domain: CreditAccount) -> CreditAccountModel:
        return CreditAccountModel(
            id=str(domain.id),
            user_id=str(domain.user_id),
            available_balance=int(domain.balance.available),
            reserved_balance=int(domain.balance.reserved),
            grants=[CreditGrantORMMapper.to_model(grant) for grant in domain.grants],
            ledger_entries=[
                CreditLedgerEntryORMMapper.to_model(entry)
                for entry in domain.ledger_entries
            ],
        )

    @staticmethod
    def update_model(
        model: CreditAccountModel,
        domain: CreditAccount,
    ) -> CreditAccountModel:
        model.user_id = str(domain.user_id)
        model.available_balance = int(domain.balance.available)
        model.reserved_balance = int(domain.balance.reserved)

        model.grants.clear()
        model.grants.extend(
            CreditGrantORMMapper.to_model(grant) for grant in domain.grants
        )

        model.ledger_entries.clear()
        model.ledger_entries.extend(
            CreditLedgerEntryORMMapper.to_model(entry)
            for entry in domain.ledger_entries
        )

        return model


class CreditGrantORMMapper:
    @staticmethod
    def from_model(model: CreditGrantModel) -> CreditGrant:
        return CreditGrant(
            id=CreditGrantId(model.id),
            credit_account_id=CreditAccountId(model.credit_account_id),
            amount=Credits.of(model.amount),
            remaining=Credits.of(model.remaining),
            granted_at=model.granted_at,
            expires_at=model.expires_at,
            source_id=model.source_id,
        )

    @staticmethod
    def to_model(domain: CreditGrant) -> CreditGrantModel:
        return CreditGrantModel(
            id=str(domain.id),
            credit_account_id=str(domain.credit_account_id),
            amount=int(domain.amount),
            remaining=int(domain.remaining),
            granted_at=domain.granted_at,
            expires_at=domain.expires_at,
            source_id=domain.source_id,
        )


class CreditLedgerEntryORMMapper:
    @staticmethod
    def from_model(model: CreditLedgerEntryModel) -> CreditLedgerEntry:
        return CreditLedgerEntry(
            id=CreditLedgerEntryId(model.id),
            credit_account_id=CreditAccountId(model.credit_account_id),
            delta=model.delta,
            balance_after_available=Credits.of(model.balance_after_available),
            balance_after_reserved=Credits.of(model.balance_after_reserved),
            source_type=CreditSourceType(model.source_type),
            source_id=model.source_id,
            description=model.description,
            occurred_at=model.occurred_at,
        )

    @staticmethod
    def to_model(domain: CreditLedgerEntry) -> CreditLedgerEntryModel:
        return CreditLedgerEntryModel(
            id=str(domain.id),
            credit_account_id=str(domain.credit_account_id),
            delta=int(domain.delta),
            balance_after_available=int(domain.balance_after_available),
            balance_after_reserved=int(domain.balance_after_reserved),
            source_type=domain.source_type,
            source_id=domain.source_id,
            description=domain.description,
            occurred_at=domain.occurred_at,
        )
