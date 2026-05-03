from datetime import datetime

from db.app_db import AppBase
from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class SubscriptionModel(AppBase):
    __tablename__ = "subscriptions"

    subscription_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    # plan_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    plan_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    current_period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    current_period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    cancel_at_period_end: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    provider_subscription_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )
    last_granted_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    items = relationship(
        "SubscriptionItemModel",
        back_populates="subscription",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
