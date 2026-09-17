"""Permet plusieurs services cibles par tag

Revision ID: 495484372615
Revises: 3ff2098b6a9d
Create Date: 2026-09-17 21:53:11.864702

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '495484372615'
down_revision = '3ff2098b6a9d'
branch_labels = None
depends_on = None


def upgrade():
    # Ajout temporaire de la nouvelle colonne en nullable
    # afin de pouvoir migrer les tags déjà existants.
    with op.batch_alter_table("tags", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "target_services",
                sa.JSON(),
                nullable=True
            )
        )

    # Conversion de l'ancien service unique vers une liste de services.
    #
    # Exemple :
    # "Scolarité" -> ["Scolarité"]
    #
    # Les tags sans service deviennent [].
    op.execute("""
        UPDATE tags
        SET target_services =
            CASE
                WHEN target_service IS NULL THEN '[]'::json
                ELSE json_build_array(target_service)
            END
    """)

    # La colonne est maintenant renseignée pour toutes les lignes :
    # elle peut devenir obligatoire et l'ancienne peut être supprimée.
    with op.batch_alter_table("tags", schema=None) as batch_op:
        batch_op.alter_column(
            "target_services",
            existing_type=sa.JSON(),
            nullable=False
        )
        batch_op.drop_column("target_service")


def downgrade():
    # Recréation de l'ancienne colonne à service unique.
    with op.batch_alter_table("tags", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "target_service",
                sa.String(length=100),
                nullable=True
            )
        )

    # En cas de retour arrière, seul le premier service peut être conservé
    # puisque l'ancien modèle ne supportait qu'un service par tag.
    op.execute("""
        UPDATE tags
        SET target_service =
            CASE
                WHEN json_array_length(target_services) > 0
                THEN target_services ->> 0
                ELSE NULL
            END
    """)

    with op.batch_alter_table("tags", schema=None) as batch_op:
        batch_op.drop_column("target_services")
