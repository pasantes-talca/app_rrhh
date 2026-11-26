"""Baseline del esquema rrhh existente.

Revision ID: 20261125_baseline
Create Date: 2026-11-25

Esta revisión no crea ni elimina objetos. Debe aplicarse exclusivamente con
``alembic stamp`` después de verificar que el esquema corporativo existente
coincide con los modelos auditados.
"""

revision = "20261125_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
