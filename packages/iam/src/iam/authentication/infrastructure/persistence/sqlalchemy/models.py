from uuid import UUID

from sqlalchemy import ForeignKey, Index, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from db.app_db import AppBase


class CredentialModel(AppBase):
    __tablename__ = "iam_credentials"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "type",
            name="uq_user_credential_type",
        ),
        Index(
            "ix_credential_user_type",
            "user_id",
            "type",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "iam_users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    type: Mapped[CredentialType] = mapped_column(
        Enum(
            CredentialType,
            name="credential_type",
        ),
        nullable=False,
        index=True,
    )

    secret_hash: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    status: Mapped[CredentialStatus] = mapped_column(
        Enum(
            CredentialStatus,
            name="credential_status",
        ),
        nullable=False,
    )

    attributes: Mapped[dict[str, Any] | None] = mapped_column(
        MutableDict.as_mutable(JSONB),
        nullable=True,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped[UserModel] = relationship(
        back_populates="credentials",
    )
