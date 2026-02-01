import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from db.models.base import Base


class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        Index("ix_auth_sessions_token_hash", "token_hash"),
        {"schema": "auth"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )

    token_hash: Mapped[bytes] = mapped_column(
        LargeBinary(32),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
