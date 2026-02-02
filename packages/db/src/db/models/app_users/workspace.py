import uuid

from sqlalchemy import Boolean, CheckConstraint, String
from db.models.base import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID


class Workspace(Base, TimestampMixin):
    __tablename__ = "workspaces"
    __table_args__ = (
        CheckConstraint(r"slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'", name="ck_workspaces_slug_format"),
        {"schema": "tenant"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
