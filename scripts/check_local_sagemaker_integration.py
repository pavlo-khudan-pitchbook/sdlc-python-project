"""
Smoke-check the S3 + SageMaker integration against the local moto stack.

Uploads a tiny labelled dataset, starts a training job pointing at it, and waits for the job
to reach a terminal state. Useful for checking boto3 request shapes without touching AWS.

Usage:
    docker compose up -d aws
    uv run scripts/check_local_sagemaker_integration.py
"""

import datetime as dt
import sys
import time

import boto3

# Hardcoded to the local docker-compose stack (see docker-compose.yml)
AWS_ENDPOINT_URL = "http://localhost:4566"
AWS_REGION = "us-east-1"
TRAINING_DATA_S3_BUCKET = "local-training-data"
MODEL_ARTIFACTS_S3_BUCKET = "local-model-artifacts"
SAGEMAKER_ROLE_ARN = "arn:aws:iam::123456789012:role/local-sagemaker-role"
TRAINING_IMAGE_URI = (
    "123456789012.dkr.ecr.us-east-1.amazonaws.com/ticket-classifier-training:latest"
)
TIMEOUT_S = 60

SAMPLE_CSV = """ticket_id,subject,body,customer_email,category
T-1,Where is my order?,It has been 10 days,a@example.com,shipping
T-2,Refund please,Item arrived broken,b@example.com,refund
"""


def _client(service: str):
    return boto3.client(
        service,
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",  # noqa: S106
    )


def main() -> int:
    s3 = _client("s3")
    sagemaker = _client("sagemaker")

    for bucket in (TRAINING_DATA_S3_BUCKET, MODEL_ARTIFACTS_S3_BUCKET):
        s3.create_bucket(Bucket=bucket)

    run_id = dt.datetime.now(dt.UTC).strftime("%Y%m%d-%H%M%S")
    prefix = f"training-data/smoke-{run_id}/"
    s3.put_object(
        Bucket=TRAINING_DATA_S3_BUCKET, Key=f"{prefix}train.csv", Body=SAMPLE_CSV
    )
    print(f"Uploaded sample dataset to s3://{TRAINING_DATA_S3_BUCKET}/{prefix}")

    job_name = f"smoke-check-{run_id}"
    sagemaker.create_training_job(
        TrainingJobName=job_name,
        AlgorithmSpecification={
            "TrainingImage": TRAINING_IMAGE_URI,
            "TrainingInputMode": "File",
        },
        RoleArn=SAGEMAKER_ROLE_ARN,
        InputDataConfig=[
            {
                "ChannelName": "train",
                "DataSource": {
                    "S3DataSource": {
                        "S3DataType": "S3Prefix",
                        "S3Uri": f"s3://{TRAINING_DATA_S3_BUCKET}/{prefix}",
                    }
                },
            }
        ],
        OutputDataConfig={"S3OutputPath": f"s3://{MODEL_ARTIFACTS_S3_BUCKET}/models/"},
        ResourceConfig={
            "InstanceType": "ml.m5.xlarge",
            "InstanceCount": 1,
            "VolumeSizeInGB": 30,
        },
        StoppingCondition={"MaxRuntimeInSeconds": 600},
    )
    print(f"Started training job {job_name}")

    deadline = time.monotonic() + TIMEOUT_S
    while time.monotonic() < deadline:
        status = sagemaker.describe_training_job(TrainingJobName=job_name)[
            "TrainingJobStatus"
        ]
        print(f"  status={status}")
        if status in {"Completed", "Failed", "Stopped"}:
            return 0 if status == "Completed" else 1
        time.sleep(2)

    print(f"Training job {job_name} did not finish within {TIMEOUT_S}s")
    return 1


if __name__ == "__main__":
    sys.exit(main())
