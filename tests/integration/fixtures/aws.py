from __future__ import annotations

import urllib.request
from typing import TYPE_CHECKING, Any

import boto3
import pytest

from tests.integration.config import (
    AWS_ENDPOINT_URL,
    AWS_REGION,
    MODEL_ARTIFACTS_S3_BUCKET,
    TRAINING_DATA_S3_BUCKET,
)

if TYPE_CHECKING:
    from collections.abc import Generator


def _client(service: str) -> Any:
    return boto3.client(
        service,
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",  # noqa: S106
    )


def _reset_moto() -> None:
    """moto keeps state between tests; wipe it so every test starts clean."""
    request = urllib.request.Request(  # noqa: S310
        f"{AWS_ENDPOINT_URL}/moto-api/reset", method="POST"
    )
    urllib.request.urlopen(request, timeout=5)  # noqa: S310


@pytest.fixture
def s3_client(docker_stack: None) -> Any:
    return _client("s3")


@pytest.fixture
def sagemaker_client(docker_stack: None) -> Any:
    return _client("sagemaker")


@pytest.fixture
def s3_buckets(s3_client: Any) -> Generator[None]:
    for bucket in (TRAINING_DATA_S3_BUCKET, MODEL_ARTIFACTS_S3_BUCKET):
        s3_client.create_bucket(Bucket=bucket)
    yield
    _reset_moto()
