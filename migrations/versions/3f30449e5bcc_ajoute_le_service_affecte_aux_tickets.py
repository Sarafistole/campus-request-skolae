"""Ajoute le service affecte aux tickets

Revision ID: 3f30449e5bcc
Revises: 74e9fc127c7c
Create Date: 2026-09-18 00:04:03.880640

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3f30449e5bcc"
down_revision = "74e9fc127c7c"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("tickets", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "assigned_service_id",
                sa.Integer(),
                nullable=True
            )
        )

        batch_op.create_foreign_key(
            "fk_tickets_assigned_service_id_services",
            "services",
            ["assigned_service_id"],
            ["id"]
        )


def downgrade():
    with op.batch_alter_table("tickets", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_tickets_assigned_service_id_services",
            type_="foreignkey"
        )

        batch_op.drop_column("assigned_service_id")