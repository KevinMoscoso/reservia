"""create notifications table and reminder columns

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notificaciones",
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column("user_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column(
            "tipo",
            sa.Enum(
                "reserva_confirmada", "cita_confirmada", "recordatorio",
                name="tiponotificacion",
            ),
            nullable=False,
        ),
        sa.Column("mensaje", sa.String(length=255), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=True),
        sa.Column("entity_id", mysql.BIGINT(unsigned=True), nullable=True),
        sa.Column("leida", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column(
        "reservas_salas",
        sa.Column("recordatorio_enviado", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "reservas_equipos",
        sa.Column("recordatorio_enviado", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "citas",
        sa.Column("recordatorio_enviado", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("citas", "recordatorio_enviado")
    op.drop_column("reservas_equipos", "recordatorio_enviado")
    op.drop_column("reservas_salas", "recordatorio_enviado")
    op.drop_table("notificaciones")