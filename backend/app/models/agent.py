"""Agent-related models — runs, schedule, feedback, and embeddings.

These tables are created in the initial migration to avoid future schema
changes, but their API endpoints are built in Phases 2–4.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PostEmbedding(Base):
    """Vector embeddings for semantic search over posts (Phase 2)."""

    __tablename__ = "post_embeddings"

    post_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
    )
    # embedding column is VECTOR(1536) — added via raw SQL in migration
    # since pgvector types require the extension to be enabled first.
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now,
        nullable=False,
    )


class ContextEmbedding(Base):
    """Vector embeddings for author context fields (Phase 2)."""

    __tablename__ = "context_embeddings"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("owners.id"),
        nullable=False,
    )
    field_key: Mapped[str] = mapped_column(Text, nullable=False)
    # embedding column is VECTOR(1536) — added via raw SQL in migration.
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )


class PostFeedback(Base):
    """Author feedback on agent-generated drafts (Phase 4)."""

    __tablename__ = "post_feedback"

    post_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("posts.id"),
        nullable=False,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("owners.id"),
        nullable=False,
    )
    rating: Mapped[str] = mapped_column(Text, nullable=False)
    edit_diff: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now,
        nullable=False,
    )


class AgentRun(Base):
    """Log of each AI agent pipeline execution (Phase 3)."""

    __tablename__ = "agent_runs"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("owners.id"),
        nullable=False,
    )
    topic: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_used: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="running")
    output_post_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("posts.id"),
        nullable=True,
    )
    run_log: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    triggered_by: Mapped[str] = mapped_column(Text, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        default=datetime.now,
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)


class AgentSchedule(Base):
    """Cron schedule configuration for the agent pipeline (Phase 3)."""

    __tablename__ = "agent_schedule"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("owners.id"),
        unique=True,
        nullable=False,
    )
    cron_expr: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="0 9 * * 1",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )
