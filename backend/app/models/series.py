"""Series model — ordered grouping of related posts."""

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Series(Base):
    __tablename__ = "series"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("owners.id"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="draft",
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )

    # --- Relationships ---
    posts: Mapped[list["Post"]] = relationship(  # noqa: F821
        back_populates="series",
        lazy="noload",  # Loaded explicitly in series detail queries
        order_by="Post.series_order",
    )
