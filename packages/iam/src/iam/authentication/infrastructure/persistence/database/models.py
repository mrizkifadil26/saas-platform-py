from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column

from iam.authentication.domain import (
    AuthenticationDenialReason,
    AuthenticationOutcome,
    CredentialStatus,
    CredentialType,
)
from iam.shared.infrastructure.persistence import IAMBase


class CredentialModel(IAMBase):
    __tablename__ = "credentials"

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
        Index(
            "ix_credential_type_status",
            "type",
            "status",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
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
        index=True,
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


class AuthenticationAttemptModel(IAMBase):
    __tablename__ = "authentication_attempts"

    __table_args__ = (
        Index(
            "ix_auth_attempt_email_attempted_at",
            "email",
            "attempted_at",
        ),
        Index(
            "ix_auth_attempt_user_attempted_at",
            "user_id",
            "attempted_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        index=True,
    )

    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(45),  # ipv6 safe
        nullable=True,
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
    )

    outcome: Mapped[AuthenticationOutcome] = mapped_column(
        Enum(
            AuthenticationOutcome,
            name="authentication_outcome",
        ),
        nullable=False,
    )

    denial_reason: Mapped[AuthenticationDenialReason | None] = mapped_column(
        Enum(
            AuthenticationDenialReason,
            name="authentication_denial_reason",
        ),
        nullable=True,
    )

    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
