"""
add_rbac_enterprise_tables

Revision ID: e83f2a890db7
Revises: f7823f9b2d88
Create Date: 2026-07-08 13:00:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e83f2a890db7"
down_revision = "f7823f9b2d88"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Drop old user_roles join table if it exists to replace with full model table
    op.execute("DROP TABLE IF EXISTS user_roles CASCADE")

    # 2. Create permission_groups table
    op.create_table(
        "permission_groups",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_permission_groups_name", "permission_groups", ["name"], unique=True)

    # 3. Alter permissions table to match the expanded schema
    # First drop code column
    op.drop_column("permissions", "code")
    op.add_column("permissions", sa.Column("module", sa.String(length=100), nullable=False, server_default="users"))
    op.add_column("permissions", sa.Column("permission", sa.String(length=100), nullable=False, server_default="users.read"))
    op.add_column("permissions", sa.Column("action", sa.String(length=50), nullable=False, server_default="read"))
    op.add_column("permissions", sa.Column("category", sa.String(length=100), nullable=False, server_default="general"))
    op.add_column("permissions", sa.Column("system_permission", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("permissions", sa.Column("group_id", sa.Uuid(), nullable=True))

    op.create_index("ix_permissions_module", "permissions", ["module"], unique=False)
    op.create_index("ix_permissions_permission", "permissions", ["permission"], unique=True)
    op.create_foreign_key(
        "fk_permissions_group_id_permission_groups",
        "permissions",
        "permission_groups",
        ["group_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # 4. Alter roles table to match the expanded schema
    op.add_column("roles", sa.Column("organization_id", sa.Uuid(), nullable=True))
    op.add_column("roles", sa.Column("slug", sa.String(length=100), nullable=False, server_default="viewer"))
    op.add_column("roles", sa.Column("priority", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("roles", sa.Column("status", sa.String(length=50), nullable=False, server_default="active"))
    op.add_column("roles", sa.Column("created_by", sa.Uuid(), nullable=True))
    op.add_column("roles", sa.Column("updated_by", sa.Uuid(), nullable=True))
    op.add_column("roles", sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("roles", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    op.create_index("ix_roles_organization_id", "roles", ["organization_id"], unique=False)
    op.create_index("ix_roles_slug", "roles", ["slug"], unique=True)
    op.create_index("ix_roles_status", "roles", ["status"], unique=False)

    op.create_foreign_key("fk_roles_organization_id_organizations", "roles", "organizations", ["organization_id"], ["id"], ondelete="CASCADE")
    op.create_foreign_key("fk_roles_created_by_users", "roles", "users", ["created_by"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_roles_updated_by_users", "roles", "users", ["updated_by"], ["id"], ondelete="SET NULL")

    # 5. Create user_roles table with full audits
    op.create_table(
        "user_roles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.Column("assigned_by", sa.Uuid(), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["assigned_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_user_roles_organization_id", "user_roles", ["organization_id"], unique=False)
    op.create_index("ix_user_roles_user_id", "user_roles", ["user_id"], unique=False)
    op.create_index("ix_user_roles_role_id", "user_roles", ["role_id"], unique=False)
    op.create_index("ix_user_roles_status", "user_roles", ["status"], unique=False)

    # 6. Create role_audit_logs table
    op.create_table(
        "role_audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_role_audit_logs_organization_id", "role_audit_logs", ["organization_id"], unique=False)
    op.create_index("ix_role_audit_logs_user_id", "role_audit_logs", ["user_id"], unique=False)
    op.create_index("ix_role_audit_logs_action", "role_audit_logs", ["action"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_role_audit_logs_action", table_name="role_audit_logs")
    op.drop_index("ix_role_audit_logs_user_id", table_name="role_audit_logs")
    op.drop_index("ix_role_audit_logs_organization_id", table_name="role_audit_logs")
    op.drop_table("role_audit_logs")

    op.drop_index("ix_user_roles_status", table_name="user_roles")
    op.drop_index("ix_user_roles_role_id", table_name="user_roles")
    op.drop_index("ix_user_roles_user_id", table_name="user_roles")
    op.drop_index("ix_user_roles_organization_id", table_name="user_roles")
    op.drop_table("user_roles")

    op.drop_constraint("fk_roles_organization_id_organizations", "roles", type_="foreignkey")
    op.drop_constraint("fk_roles_created_by_users", "roles", type_="foreignkey")
    op.drop_constraint("fk_roles_updated_by_users", "roles", type_="foreignkey")
    op.drop_index("ix_roles_status", table_name="roles")
    op.drop_index("ix_roles_slug", table_name="roles")
    op.drop_index("ix_roles_organization_id", table_name="roles")
    op.drop_column("roles", "deleted_at")
    op.drop_column("roles", "is_deleted")
    op.drop_column("roles", "updated_by")
    op.drop_column("roles", "created_by")
    op.drop_column("roles", "status")
    op.drop_column("roles", "priority")
    op.drop_column("roles", "slug")
    op.drop_column("roles", "organization_id")

    op.drop_constraint("fk_permissions_group_id_permission_groups", "permissions", type_="foreignkey")
    op.drop_index("ix_permissions_permission", table_name="permissions")
    op.drop_index("ix_permissions_module", table_name="permissions")
    op.drop_column("permissions", "group_id")
    op.drop_column("permissions", "system_permission")
    op.drop_column("permissions", "category")
    op.drop_column("permissions", "action")
    op.drop_column("permissions", "permission")
    op.drop_column("permissions", "module")
    op.add_column("permissions", sa.Column("code", sa.String(length=100), nullable=False, unique=True))

    op.drop_index("ix_permission_groups_name", table_name="permission_groups")
    op.drop_table("permission_groups")
