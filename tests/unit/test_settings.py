import pytest
from pydantic import ValidationError

from retraining_job.settings import Settings

REQUIRED_ENV = {
    "ENVIRONMENT": "local",
    "DB_HOST": "localhost",
    "DB_NAME": "retraining",
    "DB_USERNAME": "user",
    "DB_PASSWORD": "secret",
    "AWS_REGION": "us-east-1",
    "TRAINING_DATA_S3_BUCKET": "training-data",
    "MODEL_ARTIFACTS_S3_BUCKET": "model-artifacts",
    "SAGEMAKER_ROLE_ARN": "arn:aws:iam::123456789012:role/test",
    "TRAINING_IMAGE_URI": "image:latest",
}


def test_settings_load_from_env(monkeypatch: pytest.MonkeyPatch):
    for key, value in REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)

    settings = Settings()

    assert settings.db_port == 5432
    assert settings.training_instance_type == "ml.m5.xlarge"


def test_secrets_are_not_in_repr(monkeypatch: pytest.MonkeyPatch):
    for key, value in REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)

    assert "secret" not in repr(Settings())


def test_missing_required_setting_fails(monkeypatch: pytest.MonkeyPatch):
    for key, value in REQUIRED_ENV.items():
        if key != "DB_HOST":
            monkeypatch.setenv(key, value)
    monkeypatch.delenv("DB_HOST", raising=False)

    with pytest.raises(ValidationError):
        Settings()
