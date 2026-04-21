from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from db.models.base import Base


class SubscriptionModel(Base):
    __tablename__ = "subscriptions"

    subscription_id: Mapped[str] = mapped_column(
        String(36), primary_key=True
    )
    user_id: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False
    )
    plan_code: Mapped[str] = mapped_column(
        String(128), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False
    )
    current_period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    current_period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    cancel_at_period_end: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    provider_subscription_id: Mapped[str | None] = (
        mapped_column(String(255), nullable=True)
    )
    last_granted_period_start: Mapped[datetime | None] = (
        mapped_column(
            DateTime(timezone=True), nullable=True
        )
    )
