from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from db import AppBase
from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column


class PaygPurchaseModel(AppBase):
    __tablename__ = "billing_payg_purchases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    user_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    pack_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    credits: Mapped[int] = mapped_column(nullable=False)
    price_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 6),
        nullable=False,
    )
    price_currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )
    expires_in_days: Mapped[int] = mapped_column(nullable=False)

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    credits_granted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    failed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    refunded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    failure_reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
