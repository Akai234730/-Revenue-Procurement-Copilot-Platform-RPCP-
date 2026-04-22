from sqlalchemy import Column, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import BaseEntity

user_role_association = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String(64), ForeignKey("users.id"), primary_key=True),
    Column("role_id", String(64), ForeignKey("roles.id"), primary_key=True),
)

role_permission_association = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", String(64), ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", String(64), ForeignKey("permissions.id"), primary_key=True),
)


class User(BaseEntity):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(128))
    email: Mapped[str] = mapped_column(String(255), default="")
    password_hash: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(32), default="active")
    dept_id: Mapped[str] = mapped_column(String(64), default="")
    title: Mapped[str] = mapped_column(String(128), default="")
    roles: Mapped[list["Role"]] = relationship(secondary=user_role_association, back_populates="users")


class Role(BaseEntity):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    users: Mapped[list[User]] = relationship(secondary=user_role_association, back_populates="roles")
    permissions: Mapped[list["Permission"]] = relationship(
        secondary=role_permission_association, back_populates="roles"
    )


class Permission(BaseEntity):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(64), unique=True)
    code: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    roles: Mapped[list[Role]] = relationship(
        secondary=role_permission_association, back_populates="permissions"
    )
