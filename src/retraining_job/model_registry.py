from __future__ import annotations

from typing import TYPE_CHECKING

from psycopg.types.json import Jsonb
from structlog import get_logger

from retraining_job.database.sql import DEMOTE_CHAMPIONS, INSERT_MODEL, PROMOTE_MODEL

if TYPE_CHECKING:
    from retraining_job.database import PostgresDB
    from retraining_job.sagemaker import TrainingResult

logger = get_logger()


class ModelRegistry:
    """Postgres-backed registry of trained classifier models.

    The serving side loads whichever model is flagged as `is_champion`.
    """

    def __init__(self, db: PostgresDB):
        self._db = db

    def register(
        self,
        model_name: str,
        model_version: str,
        training: TrainingResult,
        training_data_s3_uri: str,
    ) -> str:
        with self._db.connection() as conn, conn.cursor() as cur:
            cur.execute(
                INSERT_MODEL,
                {
                    "model_name": model_name,
                    "model_version": model_version,
                    "training_job_name": training.job_name,
                    "artifact_s3_uri": training.model_artifact_s3_uri,
                    "training_data_s3_uri": training_data_s3_uri,
                    "metrics": Jsonb(training.metrics),
                },
            )
            row = cur.fetchone()

        if row is None:
            raise RuntimeError(f"Failed to register model {model_name}:{model_version}")
        model_id = str(row["model_id"])
        logger.info(
            f"Registered model {model_name}:{model_version} as model_id={model_id}"
        )
        return model_id

    def promote(self, model_name: str, model_id: str) -> None:
        """Make the given model the champion; demotes the previous one atomically."""
        with self._db.connection() as conn, conn.cursor() as cur:
            cur.execute(DEMOTE_CHAMPIONS, {"model_name": model_name})
            cur.execute(PROMOTE_MODEL, {"model_id": model_id})
        logger.info(f"Promoted model_id={model_id} to champion")
