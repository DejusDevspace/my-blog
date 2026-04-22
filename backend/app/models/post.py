"""Post and Tag models with many-to-many association."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PostTag(Base):
    """Association table for the many-to-many post ↔ tag relationship."""

    __tablename__ = "post_tags"
    __table_args__ = (
        UniqueConstraint("post_id", "tag_id", name="uq_post_tags_post_tag"),
    )

    post_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False,
    )


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("owner_id", "slug", name="uq_tags_owner_slug"),
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("owners.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, nullable=False)

    # --- Relationships ---
    posts: Mapped[list["Post"]] = relationship(
        secondary="post_tags",
        back_populates="tags",
        lazy="selectin",
    )


class Post(Base):
    __tablename__ = "posts"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("owners.id"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="draft",
    )
    is_agent_authored: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    reading_time_mins: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    published_at: Mapped[datetime | None] = mapped_column(nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)
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
    category: Mapped["Category"] = relationship(  # noqa: F821
        back_populates="posts",
        lazy="selectin",
    )
    tags: Mapped[list[Tag]] = relationship(
        secondary="post_tags",
        back_populates="posts",
        lazy="selectin",
    )
    comments: Mapped[list["Comment"]] = relationship(  # noqa: F821
        back_populates="post",
        lazy="selectin",
    )
