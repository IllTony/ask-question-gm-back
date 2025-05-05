import datetime as dt
from uuid import UUID

from sqlalchemy import text, ForeignKey
from sqlalchemy.orm import declared_attr, mapped_column, Mapped, declarative_mixin


@declarative_mixin
class ActivityMixin:
    is_active: Mapped[bool] = mapped_column(default=True, nullable=True)


class ModelHistoryMixin:
    @declared_attr
    def created_at(cls) -> Mapped[dt.datetime]:
        return mapped_column(server_default=text("TIMEZONE('utc', now())"))

    @declared_attr
    def updated_at(cls) -> Mapped[dt.datetime]:
        return mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=dt.datetime.utcnow)

    @declared_attr
    def creator_id(cls) -> Mapped[UUID]:
        return mapped_column(
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
            default=None,
        )

    @declared_attr
    def modifier_id(cls) -> Mapped[UUID]:
        return mapped_column(
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
            default=None,
        )
