"""Add champion flag to classifier model registry

Revision ID: 7f8e9d0c1b2a
Revises: 1a2b3c4d5e6f
Create Date: 2026-08-19 15:02:47.530914

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7f8e9d0c1b2a"
down_revision: str | Sequence[str] | None = "1a2b3c4d5e6f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "classifier_model_registry",
        sa.Column("is_champion", sa.Boolean(), server_default=sa.false(), nullable=False),
        schema="retraining",
    )
    op.add_column(
        "classifier_model_registry",
        sa.Column("promoted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        schema="retraining",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("classifier_model_registry", "promoted_at", schema="retraining")
    op.drop_column("classifier_model_registry", "is_champion", schema="retraining")
