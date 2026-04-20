import uuid
from datetime import datetime

from packages.shared.db.src.db.models.base import Base, TimestampMixin
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column


class WorkspaceEntitlement(Base, TimestampMixin):
    __tablename__ = "workspace_entitlements"
    __table_args__ = (
        CheckConstraint(
            "(monthly_lookup_limit IS NULL OR monthly_lookup_limit >= 0) AND "
            "(monthly_enrich_limit IS NULL OR monthly_enrich_limit >= 0)",
            name="ck_entitlements_limits_nonneg",
        ),
        {"schema": "entitlements"},
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.workspaces.id", ondelete="CASCADE"),
        primary_key=True,
    )

    plan: Mapped[str] = mapped_column(String, nullable=False, default="free")
    status: Mapped[str] = mapped_column(String, nullable=False, default="active")

    monthly_lookup_limit: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=None,
    )
    monthly_enrich_limit: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=None,
    )

    features: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
