from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, PrimaryKeyConstraint, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from iam.shared.infrastructure.persistence import IAMBase


class RoleModel(IAMBase):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    permissions = relationship(
        "RolePermissionModel",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class UserRoleModel(IAMBase):
    __tablename__ = "user_roles"

    __table_args__ = (
        PrimaryKeyConstraint(
            "user_id",
            "role_id",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    role_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey(
            "roles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class RolePermissionModel(IAMBase):
    __tablename__ = "role_permissions"

    __table_args__ = (
        PrimaryKeyConstraint(
            "role_id",
            "permission",
        ),
    )

    role_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey(
            "roles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    permission: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
