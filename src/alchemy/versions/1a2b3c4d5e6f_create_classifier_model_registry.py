"""Create classifier model registry table

Revision ID: 1a2b3c4d5e6f
Revises: -
Create Date: 2026-07-02 10:41:09.118342

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "1a2b3c4d5e6f"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE SCHEMA IF NOT EXISTS retraining")  # added manually
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")  # added manually

    op.create_table(
        "classifier_model_registry",
        sa.Column(
            "model_id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("model_name", sa.Text(), nullable=False),
        sa.Column("model_version", sa.Text(), nullable=False),
        sa.Column("training_job_name", sa.Text(), nullable=False),
        sa.Column("artifact_s3_uri", sa.Text(), nullable=False),
        sa.Column("training_data_s3_uri", sa.Text(), nullable=False),
        sa.Column(
            "metrics",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("model_id"),
        sa.UniqueConstraint(
            "model_name", "model_version", name="classifier_model_registry_uniq"
        ),
        schema="retraining",
        comment="Registry of classifier models trained by the retraining cronjob.",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("classifier_model_registry", schema="retraining")
