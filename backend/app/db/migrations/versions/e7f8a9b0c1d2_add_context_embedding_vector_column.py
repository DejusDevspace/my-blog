"""add context embedding vector column to context_embeddings

Revision ID: e7f8a9b0c1d2
Revises: d4e5f6a7b8c9
Create Date: 2026-06-06 14:00:00.000000

Adds the VECTOR(384) column to context_embeddings and an HNSW index
for fast cosine similarity queries.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "e7f8a9b0c1d2"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "context_embeddings",
        sa.Column("embedding", Vector(384), nullable=True),
    )
    op.create_index(
        "ix_context_embeddings_embedding_hnsw",
        "context_embeddings",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_with={"m": 16, "ef_construction": 64},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_index(
        "ix_context_embeddings_embedding_hnsw", table_name="context_embeddings"
    )
    op.drop_column("context_embeddings", "embedding")
