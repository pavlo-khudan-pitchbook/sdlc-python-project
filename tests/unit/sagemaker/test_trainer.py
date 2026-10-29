from unittest.mock import MagicMock

import pytest

from retraining_job.sagemaker import SageMakerTrainer, TrainingJobConfig


@pytest.fixture
def sagemaker_client() -> MagicMock:
    return MagicMock()


def test_start_passes_training_channel(
    sagemaker_client: MagicMock, training_config: TrainingJobConfig
):
    trainer = SageMakerTrainer(sagemaker_client, training_config)

    trainer.start("job-1", "s3://bucket/training-data/run/")

    kwargs = sagemaker_client.create_training_job.call_args.kwargs
    assert kwargs["TrainingJobName"] == "job-1"
    channel = kwargs["InputDataConfig"][0]
    assert (
        channel["DataSource"]["S3DataSource"]["S3Uri"] == "s3://bucket/training-data/run/"
    )


def test_wait_polls_until_terminal_status(
    sagemaker_client: MagicMock,
    training_config: TrainingJobConfig,
    mocker,
):
    mocker.patch("retraining_job.sagemaker.trainer.time.sleep")
    sagemaker_client.describe_training_job.side_effect = [
        {"TrainingJobStatus": "InProgress"},
        {
            "TrainingJobStatus": "Completed",
            "ModelArtifacts": {"S3ModelArtifacts": "s3://bucket/model.tar.gz"},
            "FinalMetricDataList": [{"MetricName": "validation:accuracy", "Value": 0.9}],
        },
    ]
    trainer = SageMakerTrainer(sagemaker_client, training_config, poll_interval_s=0)

    result = trainer.wait("job-1")

    assert result.succeeded
    assert result.model_artifact_s3_uri == "s3://bucket/model.tar.gz"
    assert result.metrics == {"validation:accuracy": 0.9}
    assert sagemaker_client.describe_training_job.call_count == 2


def test_wait_returns_failure_reason(
    sagemaker_client: MagicMock, training_config: TrainingJobConfig
):
    sagemaker_client.describe_training_job.return_value = {
        "TrainingJobStatus": "Failed",
        "FailureReason": "AlgorithmError: out of memory",
    }
    trainer = SageMakerTrainer(sagemaker_client, training_config)

    result = trainer.wait("job-1")

    assert not result.succeeded
    assert result.failure_reason == "AlgorithmError: out of memory"
