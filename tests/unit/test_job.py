from unittest.mock import MagicMock

from retraining_job.exporter import ExportResult
from retraining_job.job import RetrainingJob
from retraining_job.sagemaker import TrainingResult


def _build_job(training_result: TrainingResult) -> tuple[RetrainingJob, MagicMock]:
    exporter = MagicMock()
    exporter.export.return_value = ExportResult(
        s3_uri="s3://test-training-data/training-data/run/", row_count=10
    )
    trainer = MagicMock()
    trainer.wait.return_value = training_result
    registry = MagicMock()
    registry.register.return_value = "model-id-1"

    job = RetrainingJob(
        exporter=exporter,
        trainer=trainer,
        registry=registry,
        model_name="ticket-classifier",
    )
    return job, registry


def test_successful_training_registers_and_promotes(completed_training: TrainingResult):
    job, registry = _build_job(completed_training)

    job.run()

    registry.register.assert_called_once()
    registry.promote.assert_called_once_with("ticket-classifier", "model-id-1")


def test_failed_training_does_not_register():
    failed = TrainingResult(
        job_name="ticket-classifier-20260101-020000",
        status="Failed",
        model_artifact_s3_uri=None,
        metrics={},
        failure_reason="AlgorithmError",
    )
    job, registry = _build_job(failed)

    job.run()

    registry.register.assert_not_called()
    registry.promote.assert_not_called()
