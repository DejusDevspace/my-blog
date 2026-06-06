"""add FTS search_vector to posts table

Revision ID: d4e5f6a7b8c9
Revises: b2932a51c440
Create Date: 2026-06-06 15:00:00.000000

Adds a tsvector column and GIN index for PostgreSQL full-text search,
plus a trigger that auto-updates the vector when title or content changes.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "b2932a51c440"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add tsvector column (nullable — populated by trigger).
    op.execute("ALTER TABLE posts ADD COLUMN search_vector tsvector")

    # GIN index for fast full-text search lookups.
    op.create_index(
        "ix_posts_search_vector_gin",
        "posts",
        ["search_vector"],
        postgresql_using="gin",
    )

    # Trigger function that auto-updates search_vector on title/content change.
    op.execute("""
        CREATE OR REPLACE FUNCTION posts_search_vector_update()
        RETURNS trigger AS $$
        BEGIN
            NEW.search_vector := to_tsvector('english',
                coalesce(NEW.title, '') || ' ' || coalesce(NEW.content, ''));
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Apply the trigger — fires BEFORE INSERT or when title/content is updated.
    op.execute("""
        CREATE TRIGGER trg_posts_search_vector
        BEFORE INSERT OR UPDATE OF title, content ON posts
        FOR EACH ROW
        EXECUTE FUNCTION posts_search_vector_update();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_posts_search_vector ON posts")
    op.execute("DROP FUNCTION IF EXISTS posts_search_vector_update()")
    op.drop_index("ix_posts_search_vector_gin", table_name="posts")
    op.drop_column("posts", "search_vector")
