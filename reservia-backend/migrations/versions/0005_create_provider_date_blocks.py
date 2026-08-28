"""create provider_date_blocks table

Revision ID: 0005
Revises: 0004
Create Date: 2026-08-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "provider_date_blocks",
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column("provider_profile_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("motivo", sa.String(length=255), nullable=True),
        sa.Column(
            "estado",
            sa.Enum("active", "inactive", name="datablockestado"),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            server_onupdate=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["provider_profile_id"], ["provider_profiles.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("provider_date_blocks")