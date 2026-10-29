from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest

from retraining_job.sagemaker import TrainingJobConfig, TrainingResult

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture
def training_config() -> TrainingJobConfig:
    return TrainingJobConfig(
        role_arn="arn:aws:iam::123456789012:role/test-role",
        image_uri="123456789012.dkr.ecr.us-east-1.amazonaws.com/ticket-classifier:test",
        instance_type="ml.m5.xlarge",
        max_runtime_s=600,
        output_s3_uri="s3://test-model-artifacts/models/",
    )


@pytest.fixture
def completed_training() -> TrainingResult:
    return TrainingResult(
        job_name="ticket-classifier-20260101-020000",
        status="Completed",
        model_artifact_s3_uri="s3://test-model-artifacts/models/job/output/model.tar.gz",
        metrics={"validation:accuracy": 0.91},
    )


@pytest.fixture
def mock_cursor() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_db(mock_cursor: MagicMock) -> MagicMock:
    """PostgresDB stand-in whose connection().cursor() yields `mock_cursor`."""
    conn = MagicMock()

    @contextmanager
    def _cursor() -> Iterator[MagicMock]:
        yield mock_cursor

    conn.cursor.side_effect = _cursor

    @contextmanager
    def _connection() -> Iterator[Any]:
        yield conn

    db = MagicMock()
    db.connection.side_effect = _connection
    return db
