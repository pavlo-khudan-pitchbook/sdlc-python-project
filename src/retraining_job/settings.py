from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
    )
    environment: str = Field(
        alias="ENVIRONMENT"
    )  # "local" | "k8s" | "integration_testing"
    log_level: str = Field(default="info", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")

    db_host: str = Field(alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(alias="DB_NAME")
    db_user: str = Field(alias="DB_USERNAME", repr=False)
    db_password: str = Field(alias="DB_PASSWORD", repr=False)
    db_connect_timeout: int = Field(default=10, alias="DB_CONNECT_TIMEOUT")

    aws_region: str = Field(alias="AWS_REGION")
    # Only set for local development / integration tests (moto server)
    aws_endpoint_url: str | None = Field(default=None, alias="AWS_ENDPOINT_URL")

    source_table: str = Field(default="support.ticket_labels", alias="SOURCE_TABLE")
    training_data_s3_bucket: str = Field(alias="TRAINING_DATA_S3_BUCKET")
    model_artifacts_s3_bucket: str = Field(alias="MODEL_ARTIFACTS_S3_BUCKET")

    sagemaker_role_arn: str = Field(alias="SAGEMAKER_ROLE_ARN")
    training_image_uri: str = Field(alias="TRAINING_IMAGE_URI")
    training_instance_type: str = Field(
        default="ml.m5.xlarge", alias="TRAINING_INSTANCE_TYPE"
    )
    training_max_runtime_s: int = Field(default=3600, alias="TRAINING_MAX_RUNTIME_S")
    training_poll_interval_s: int = Field(default=60, alias="TRAINING_POLL_INTERVAL_S")

    model_name: str = Field(default="ticket-classifier", alias="MODEL_NAME")
