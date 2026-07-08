"""
add_vector_tables

Revision ID: e762bef8394b
Revises: d762bef8394a
Create Date: 2026-07-08 17:00:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e762bef8394b"
down_revision = "d762bef8394a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create embedding_providers table
    op.create_table(
        "embedding_providers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_embedding_providers_code", "embedding_providers", ["code"], unique=True)

    # 2. Create embedding_models table
    op.create_table(
        "embedding_models",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("provider_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("dimensions", sa.Integer(), nullable=False, server_default="1536"),
        sa.Column("cost_per_million", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("latency_ms", sa.Integer(), nullable=False, server_default="200"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["provider_id"], ["embedding_providers.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_embedding_models_code", "embedding_models", ["code"], unique=True)

    # 3. Create vector_indexes table
    op.create_table(
        "vector_indexes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("knowledge_base_id", sa.Uuid(), nullable=False),
        sa.Column("index_type", sa.String(length=50), nullable=False, server_default="hnsw"),
        sa.Column("dimensions", sa.Integer(), nullable=False, server_default="1536"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["knowledge_base_id"], ["knowledge_bases.id"], ondelete="CASCADE"),
    )

    # 4. Create vector_search_histories table
    op.create_table(
        "vector_search_histories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("knowledge_base_id", sa.Uuid(), nullable=False),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("top_k", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("latency_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("results_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["knowledge_base_id"], ["knowledge_bases.id"], ondelete="CASCADE"),
    )

    # 5. Create vector_search_feedbacks table
    op.create_table(
        "vector_search_feedbacks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("search_history_id", sa.Uuid(), nullable=False),
        sa.Column("relevance_score", sa.Integer(), nullable=False),
        sa.Column("comments", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["search_history_id"], ["vector_search_histories.id"], ondelete="CASCADE"),
    )

    # 6. Add columns to embeddings table
    op.add_column("embeddings", sa.Column("chunk_id", sa.Uuid(), nullable=True))
    op.add_column("embeddings", sa.Column("model_id", sa.Uuid(), nullable=True))
    op.create_foreign_key("fk_embeddings_chunk_id", "embeddings", "document_chunks", ["chunk_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_embeddings_model_id", "embeddings", "embedding_models", ["model_id"], ["id"], ondelete="SET NULL")
    op.create_index("ix_embeddings_chunk_id", "embeddings", ["chunk_id"], unique=False)
    op.create_index("ix_embeddings_model_id", "embeddings", ["model_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_embeddings_model_id", table_name="embeddings")
    op.drop_index("ix_embeddings_chunk_id", table_name="embeddings")
    op.drop_constraint("fk_embeddings_model_id", "embeddings", type_="foreignkey")
    op.drop_constraint("fk_embeddings_chunk_id", "embeddings", type_="foreignkey")
    op.drop_column("embeddings", "model_id")
    op.drop_column("embeddings", "chunk_id")
    op.drop_table("vector_search_feedbacks")
    op.drop_table("vector_search_histories")
    op.drop_table("vector_indexes")
    op.drop_table("embedding_models")
    op.drop_table("embedding_providers")
