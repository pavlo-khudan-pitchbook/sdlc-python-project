"""
Integration Testing Environment Configuration.

Matches the services defined in tests/integration/docker-compose.yml.
"""

from pathlib import Path

INTEGRATION_DIR = Path(__file__).parent
REPO_ROOT = INTEGRATION_DIR.parents[1]
COMPOSE_FILE = INTEGRATION_DIR / "docker-compose.yml"

POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5433
POSTGRES_USER = "retraining_test_user"
POSTGRES_PASSWORD = "retraining_test_password"  # noqa: S105
POSTGRES_DB = "retraining_test_db"

AWS_ENDPOINT_URL = "http://localhost:4567"
AWS_REGION = "us-east-1"
TRAINING_DATA_S3_BUCKET = "test-training-data"
MODEL_ARTIFACTS_S3_BUCKET = "test-model-artifacts"

SOURCE_TABLE = "support.ticket_labels"
MODEL_NAME = "ticket-classifier"


def get_integration_env_vars() -> dict[str, str]:
    """Environment variables for running the job against the integration stack."""
    return {
        "ENVIRONMENT": "integration_testing",
        "LOG_LEVEL": "debug",
        "LOG_FORMAT": "console",
        "DB_HOST": POSTGRES_HOST,
        "DB_PORT": str(POSTGRES_PORT),
        "DB_NAME": POSTGRES_DB,
        "DB_USERNAME": POSTGRES_USER,
        "DB_PASSWORD": POSTGRES_PASSWORD,
        "AWS_REGION": AWS_REGION,
        "AWS_ENDPOINT_URL": AWS_ENDPOINT_URL,
        "AWS_ACCESS_KEY_ID": "test",
        "AWS_SECRET_ACCESS_KEY": "test",
        "SOURCE_TABLE": SOURCE_TABLE,
        "TRAINING_DATA_S3_BUCKET": TRAINING_DATA_S3_BUCKET,
        "MODEL_ARTIFACTS_S3_BUCKET": MODEL_ARTIFACTS_S3_BUCKET,
        "SAGEMAKER_ROLE_ARN": "arn:aws:iam::123456789012:role/test-sagemaker-role",
        "TRAINING_IMAGE_URI": "123456789012.dkr.ecr.us-east-1.amazonaws.com/ticket-classifier-training:test",
        "TRAINING_POLL_INTERVAL_S": "1",
        "MODEL_NAME": MODEL_NAME,
    }
