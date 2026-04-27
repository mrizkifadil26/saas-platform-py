from db.app_db import AppBase
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from billing.subscription.infrastructure.persistence.sqlalchemy.models.subscription_model import (
    SubscriptionModel,
)


class SubscriptionItemModel(AppBase):
    __tablename__ = "subscription_items"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    subscription_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("subscriptions.subscription_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_code: Mapped[str] = mapped_column(String(64), nullable=False)
    feature_code: Mapped[str] = mapped_column(String(64), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    subscription: Mapped[SubscriptionModel] = relationship(
        back_populates="items",
    )
