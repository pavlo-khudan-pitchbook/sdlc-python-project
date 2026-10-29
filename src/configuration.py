from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import boto3
import structlog

from retraining_job.database import PostgresDB
from retraining_job.exporter import TrainingDataExporter
from retraining_job.job import RetrainingJob
from retraining_job.model_registry import ModelRegistry
from retraining_job.sagemaker import SageMakerTrainer, TrainingJobConfig

if TYPE_CHECKING:
    from retraining_job.settings import Settings


def setup_logging(log_level: str, log_format: str) -> None:
    renderer = (
        structlog.dev.ConsoleRenderer()
        if log_format == "console"
        else structlog.processors.JSONRenderer()
    )
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelNamesMapping()[log_level.upper()]
        ),
    )


def get_postgres_db(settings: Settings) -> PostgresDB:
    return PostgresDB(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        dbname=settings.db_name,
        connect_timeout=settings.db_connect_timeout,
    )


def build_retraining_job(settings: Settings) -> RetrainingJob:
    """Composition root: every concrete dependency of the job is created here."""
    session = boto3.Session(region_name=settings.aws_region)
    s3_client = session.client("s3", endpoint_url=settings.aws_endpoint_url)
    sagemaker_client = session.client("sagemaker", endpoint_url=settings.aws_endpoint_url)
    db = get_postgres_db(settings)

    return RetrainingJob(
        exporter=TrainingDataExporter(
            db=db,
            s3_client=s3_client,
            bucket=settings.training_data_s3_bucket,
            source_table=settings.source_table,
        ),
        trainer=SageMakerTrainer(
            sagemaker_client=sagemaker_client,
            config=TrainingJobConfig(
                role_arn=settings.sagemaker_role_arn,
                image_uri=settings.training_image_uri,
                instance_type=settings.training_instance_type,
                max_runtime_s=settings.training_max_runtime_s,
                output_s3_uri=f"s3://{settings.model_artifacts_s3_bucket}/models/",
            ),
            poll_interval_s=settings.training_poll_interval_s,
        ),
        registry=ModelRegistry(db=db),
        model_name=settings.model_name,
    )
