import uuid
from datetime import datetime
from typing import Annotated, TypeVar

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column
from sqlalchemy.sql import func

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

uuid_ = Annotated[
    uuid.UUID,
    mapped_column(
        primary_key=True,
        server_default=func.gen_random_uuid(),
        sort_order=-999,
        comment="uuid",
    ),
]


class DateTimeMixin:
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(), server_default=func.now(), sort_order=999, comment="created_at"
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=func.now(),
        sort_order=999,
        comment="updated_at",
    )


class DeletedAtMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(sort_order=999)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    metadata = MetaData(naming_convention=convention, schema="mdp2mailservice")

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


TModel = TypeVar("TModel", bound=Base)
