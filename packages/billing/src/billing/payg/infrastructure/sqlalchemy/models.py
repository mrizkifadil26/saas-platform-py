from __future__ import annotations

from datetime import datetime

from db import AppBase

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


class PaygPurchaseModel(AppBase):
    __tablename__ = "billing_payg_purchases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    user_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    credits: Mapped[int] = mapped_column(nullable=False)

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
