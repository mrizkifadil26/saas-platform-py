from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from identity.shared.infrastructure.database import IdentityBase


class RegistrationModel(IdentityBase):
    __tablename__ = "registrations"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )

    method: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(320),
        nullable=True,
    )

    password_hash: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    email_challenges: Mapped[list["EmailChallengeModel"]] = relationship(
        back_populates="registration",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            name="uq_registrations_user_id",
        ),
    )


class EmailChallengeModel(IdentityBase):
    __tablename__ = "email_challenges"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )

    registration_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "identity.registrations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        nullable=True,
    )

    token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    purpose: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    registration: Mapped[RegistrationModel] = relationship(
        back_populates="email_challenges",
    )

    __table_args__ = (
        UniqueConstraint(
            "token_hash",
            name="uq_email_challenges_token_hash",
        ),
        Index(
            "ix_email_challenges_registration_id",
            "registration_id",
        ),
    )
