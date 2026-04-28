from __future__ import annotations

from datetime import datetime

from db import AppBase

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CreditAccountModel(AppBase):
    __tablename__ = "credit_accounts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    available_balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reserved_balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    grants: Mapped[list[CreditGrantModel]] = relationship(
        # "CreditGrantModel",
        back_populates="credit_account",
        cascade="all, delete-orphan",
        # lazy="joined",
        lazy="selectin",
    )

    ledger_entries: Mapped[list[CreditLedgerEntryModel]] = relationship(
        # "CreditLedgerEntryModel",
        back_populates="credit_account",
        cascade="all, delete-orphan",
        # lazy="joined",
        lazy="selectin",
        order_by="CreditLedgerEntryModel.occurred_at.desc()",
    )


class CreditGrantModel(AppBase):
    __tablename__ = "credit_grants"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)

    credit_account_id: Mapped[str] = mapped_column(
        ForeignKey("credit_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining: Mapped[int] = mapped_column(Integer, nullable=False)

    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    source_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    credit_account: Mapped[CreditAccountModel] = relationship(
        # "CreditAccountModel",
        back_populates="grants",
        # lazy="joined",
    )


class CreditLedgerEntryModel(AppBase):
    __tablename__ = "credit_ledger_entries"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)

    credit_account_id: Mapped[str] = mapped_column(
        ForeignKey("credit_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    amount: Mapped[int] = mapped_column(Integer, nullable=False)

    balance_after_available: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_after_reserved: Mapped[int] = mapped_column(Integer, nullable=False)

    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    credit_account: Mapped[CreditAccountModel] = relationship(
        # "CreditAccountModel",
        back_populates="ledger_entries",
        # lazy="joined",
    )
