"""add pgvector embedding columns

Revision ID: b7e2f4a91c03
Revises: a6f3ec3ae2dd
Create Date: 2026-05-26 14:00:00.000000

Adds the vector column and supporting fields to post_embeddings.
The pgvector extension must already be enabled (CREATE EXTENSION vector).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "b7e2f4a91c03"
down_revision: Union[str, None] = "a6f3ec3ae2dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure pgvector extension is enabled (idempotent).
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Clear any placeholder rows — the table was created as a shell in the
    # initial migration but no real embedding data exists yet.
    op.execute("DELETE FROM post_embeddings")

    # Add the new columns.
    op.add_column(
        "post_embeddings",
        sa.Column("chunk_index", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "post_embeddings",
        sa.Column("chunk_text", sa.Text(), nullable=False, server_default=""),
    )
    op.add_column(
        "post_embeddings",
        sa.Column("embedding", Vector(384), nullable=True),
    )

    # Remove the temporary server defaults now that the column exists.
    op.alter_column("post_embeddings", "chunk_index", server_default=None)
    op.alter_column("post_embeddings", "chunk_text", server_default=None)

    # Create HNSW index for fast cosine similarity search.
    op.create_index(
        "ix_post_embeddings_embedding_hnsw",
        "post_embeddings",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_with={"m": 16, "ef_construction": 64},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_index(
        "ix_post_embeddings_embedding_hnsw", table_name="post_embeddings"
    )
    op.drop_column("post_embeddings", "embedding")
    op.drop_column("post_embeddings", "chunk_text")
    op.drop_column("post_embeddings", "chunk_index")
