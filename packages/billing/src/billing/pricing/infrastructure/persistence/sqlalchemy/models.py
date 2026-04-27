from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from db.app_db import AppBase

from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column


class PricingRuleModel(AppBase):
    __tablename__ = "pricing_rules"

    id: Mapped[UUID] = mapped_column(primary_key=True)

    pricing_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    billing_scheme: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    active_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    active_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
