"""create resources and providers tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "salas",
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(length=150), nullable=False),
        sa.Column("ubicacion", sa.String(length=255), nullable=False),
        sa.Column("capacidad", mysql.INTEGER(unsigned=True), nullable=False),
        sa.Column(
            "estado",
            sa.Enum("active", "inactive", name="salaestado"),
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
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "equipos",
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(length=150), nullable=False),
        sa.Column("codigo", sa.String(length=100), nullable=False),
        sa.Column("categoria", sa.String(length=100), nullable=False),
        sa.Column(
            "estado",
            sa.Enum("active", "inactive", name="equipoestado"),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo"),
    )

    op.create_table(
        "provider_profiles",
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column("user_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column(
            "slot_duration_minutes",
            mysql.SMALLINT(unsigned=True),
            nullable=False,
            server_default="30",
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "provider_schedules",
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column("provider_profile_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column(
            "day_of_week",
            sa.Enum(
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
                name="dayofweek",
            ),
            nullable=False,
        ),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column(
            "estado",
            sa.Enum("active", "inactive", name="scheduleestado"),
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
    op.drop_table("provider_schedules")
    op.drop_table("provider_profiles")
    op.drop_table("equipos")
    op.drop_table("salas")