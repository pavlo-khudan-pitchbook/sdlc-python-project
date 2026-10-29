from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from structlog import get_logger

from retraining_job.metrics import JOB_DURATION_SECONDS, TRAINING_RUNS

if TYPE_CHECKING:
    from retraining_job.exporter import TrainingDataExporter
    from retraining_job.model_registry import ModelRegistry
    from retraining_job.sagemaker import SageMakerTrainer

logger = get_logger()


class RetrainingJob:
    """Export labelled tickets -> train on SageMaker -> register and promote the model."""

    def __init__(
        self,
        exporter: TrainingDataExporter,
        trainer: SageMakerTrainer,
        registry: ModelRegistry,
        model_name: str,
    ):
        self._exporter = exporter
        self._trainer = trainer
        self._registry = registry
        self._model_name = model_name

    @JOB_DURATION_SECONDS.time()
    def run(self) -> None:
        run_id = dt.datetime.now(dt.UTC).strftime("%Y%m%d-%H%M%S")
        logger.info(f"Starting retraining run run_id={run_id}")

        export = self._exporter.export(run_id)

        job_name = f"{self._model_name}-{run_id}"
        self._trainer.start(job_name, export.s3_uri)
        result = self._trainer.wait(job_name)
        TRAINING_RUNS.labels(status=result.status).inc()

        if not result.succeeded:
            logger.error(
                f"Training job {job_name} finished with status={result.status}, "
                f"reason={result.failure_reason}"
            )
            return

        model_id = self._registry.register(
            model_name=self._model_name,
            model_version=run_id,
            training=result,
            training_data_s3_uri=export.s3_uri,
        )
        self._registry.promote(self._model_name, model_id)
        logger.info(f"Retraining run {run_id} finished, metrics={result.metrics}")
