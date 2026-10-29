from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from structlog import get_logger

logger = get_logger()

COMPLETED = "Completed"
TERMINAL_STATUSES = {COMPLETED, "Failed", "Stopped"}


@dataclass(frozen=True)
class TrainingJobConfig:
    role_arn: str
    image_uri: str
    instance_type: str
    max_runtime_s: int
    output_s3_uri: str
    hyperparameters: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class TrainingResult:
    job_name: str
    status: str
    model_artifact_s3_uri: str | None
    metrics: dict[str, float]
    failure_reason: str | None = None

    @property
    def succeeded(self) -> bool:
        return self.status == COMPLETED


class SageMakerTrainer:
    """Launches a SageMaker training job and waits for it to reach a terminal state."""

    def __init__(
        self,
        sagemaker_client: Any,
        config: TrainingJobConfig,
        poll_interval_s: int = 60,
    ):
        self._client = sagemaker_client
        self._config = config
        self._poll_interval_s = poll_interval_s

    def start(self, job_name: str, training_data_s3_uri: str) -> None:
        self._client.create_training_job(
            TrainingJobName=job_name,
            AlgorithmSpecification={
                "TrainingImage": self._config.image_uri,
                "TrainingInputMode": "File",
            },
            RoleArn=self._config.role_arn,
            InputDataConfig=[
                {
                    "ChannelName": "train",
                    "DataSource": {
                        "S3DataSource": {
                            "S3DataType": "S3Prefix",
                            "S3Uri": training_data_s3_uri,
                            "S3DataDistributionType": "FullyReplicated",
                        }
                    },
                    "ContentType": "text/csv",
                }
            ],
            OutputDataConfig={"S3OutputPath": self._config.output_s3_uri},
            ResourceConfig={
                "InstanceType": self._config.instance_type,
                "InstanceCount": 1,
                "VolumeSizeInGB": 30,
            },
            StoppingCondition={"MaxRuntimeInSeconds": self._config.max_runtime_s},
            HyperParameters=self._config.hyperparameters,
        )
        logger.info(f"Started SageMaker training job {job_name}")

    def wait(self, job_name: str) -> TrainingResult:
        while True:
            description = self._client.describe_training_job(TrainingJobName=job_name)
            status = description["TrainingJobStatus"]
            if status in TERMINAL_STATUSES:
                return self._to_result(job_name, description)

            logger.info(
                f"Training job {job_name} is {status}, checking again in {self._poll_interval_s}s"
            )
            time.sleep(self._poll_interval_s)

    @staticmethod
    def _to_result(job_name: str, description: dict[str, Any]) -> TrainingResult:
        return TrainingResult(
            job_name=job_name,
            status=description["TrainingJobStatus"],
            model_artifact_s3_uri=description.get("ModelArtifacts", {}).get(
                "S3ModelArtifacts"
            ),
            metrics={
                metric["MetricName"]: metric["Value"]
                for metric in description.get("FinalMetricDataList", [])
            },
            failure_reason=description.get("FailureReason"),
        )
