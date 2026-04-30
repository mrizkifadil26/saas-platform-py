from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from db import AppBase

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PaymentModel(AppBase):
    __tablename__ = "billing_payments"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)

    user_id: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )

    invoice_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("billing_invoices.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 6),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    method_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    method_provider: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    method_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )

    gateway_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    failure_reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    processing_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    succeeded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    failed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    canceled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    refunded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
