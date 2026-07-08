"""
add_organization_tenant_tables

Revision ID: f7823f9b2d88
Revises: 1bf159bfe118
Create Date: 2026-07-08 12:00:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "f7823f9b2d88"
down_revision = "1bf159bfe118"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Alter organizations table to add metadata columns
    op.add_column("organizations", sa.Column("business_type", sa.String(length=100), nullable=True))
    op.add_column("organizations", sa.Column("industry", sa.String(length=100), nullable=True))
    op.add_column("organizations", sa.Column("company_size", sa.String(length=50), nullable=True))
    op.add_column("organizations", sa.Column("email", sa.String(length=255), nullable=True))
    op.add_column("organizations", sa.Column("phone", sa.String(length=50), nullable=True))
    op.add_column("organizations", sa.Column("website", sa.String(length=255), nullable=True))
    op.add_column("organizations", sa.Column("country", sa.String(length=100), nullable=True))
    op.add_column("organizations", sa.Column("state", sa.String(length=100), nullable=True))
    op.add_column("organizations", sa.Column("city", sa.String(length=100), nullable=True))
    op.add_column("organizations", sa.Column("timezone", sa.String(length=100), nullable=True))
    op.add_column("organizations", sa.Column("language", sa.String(length=100), nullable=True))
    op.add_column("organizations", sa.Column("currency", sa.String(length=10), nullable=True))
    op.add_column("organizations", sa.Column("logo_url", sa.String(length=1024), nullable=True))
    op.add_column("organizations", sa.Column("brand_colors", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("organizations", sa.Column("owner_id", sa.Uuid(), nullable=True))

    op.create_foreign_key(
        "fk_organizations_owner_id_users",
        "organizations",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # 2. Create organization_settings table
    op.create_table(
        "organization_settings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("theme", sa.String(length=50), nullable=True, server_default="dark"),
        sa.Column("brand_colors", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("logo_url", sa.String(length=1024), nullable=True),
        sa.Column("business_hours", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("working_days", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("languages", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("voice_language", sa.String(length=50), nullable=True, server_default="en"),
        sa.Column("ai_personality", sa.String(length=1000), nullable=True),
        sa.Column("notification_preferences", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("whatsapp_settings", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("email_settings", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("social_media_accounts", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("custom_domain", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("custom_domain"),
    )
    op.create_index(
        "ix_organization_settings_organization_id",
        "organization_settings",
        ["organization_id"],
        unique=True,
    )

    # 3. Create organization_members table
    op.create_table(
        "organization_members",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="employee"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_organization_members_organization_id",
        "organization_members",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        "ix_organization_members_user_id",
        "organization_members",
        ["user_id"],
        unique=False,
    )

    # 4. Create organization_invitations table
    op.create_table(
        "organization_invitations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="employee"),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("invited_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["invited_by"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("token"),
    )
    op.create_index(
        "ix_organization_invitations_organization_id",
        "organization_invitations",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        "ix_organization_invitations_email",
        "organization_invitations",
        ["email"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_organization_invitations_email", table_name="organization_invitations")
    op.drop_index("ix_organization_invitations_organization_id", table_name="organization_invitations")
    op.drop_table("organization_invitations")

    op.drop_index("ix_organization_members_user_id", table_name="organization_members")
    op.drop_index("ix_organization_members_organization_id", table_name="organization_members")
    op.drop_table("organization_members")

    op.drop_index("ix_organization_settings_organization_id", table_name="organization_settings")
    op.drop_table("organization_settings")

    op.drop_constraint("fk_organizations_owner_id_users", "organizations", type_="foreignkey")
    op.drop_column("organizations", "owner_id")
    op.drop_column("organizations", "brand_colors")
    op.drop_column("organizations", "logo_url")
    op.drop_column("organizations", "currency")
    op.drop_column("organizations", "language")
    op.drop_column("organizations", "timezone")
    op.drop_column("organizations", "city")
    op.drop_column("organizations", "state")
    op.drop_column("organizations", "country")
    op.drop_column("organizations", "website")
    op.drop_column("organizations", "phone")
    op.drop_column("organizations", "email")
    op.drop_column("organizations", "company_size")
    op.drop_column("organizations", "industry")
    op.drop_column("organizations", "business_type")
