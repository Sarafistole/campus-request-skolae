"""baseline J1

Revision ID: eaabe1c5de5d
Revises:
Create Date: 2026-09-15 19:50:56.223414

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "eaabe1c5de5d"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Création de la table students telle qu'elle existait à la fin du J1
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("pseudo", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="students_email_key"),
        sa.UniqueConstraint("pseudo", name="students_pseudo_key")
    )

    # Création de la table admins telle qu'elle existait à la fin du J1
    op.create_table(
        "admins",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("service", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="admins_email_key")
    )


def downgrade():
    op.drop_table("admins")
    op.drop_table("students")