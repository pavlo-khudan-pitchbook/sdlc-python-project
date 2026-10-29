from __future__ import annotations

from typing import Any

import psycopg
import pytest

from alchemy.alembic_migrations import apply_alembic_migrations
from configuration import build_retraining_job
from retraining_job.settings import Settings
from tests.integration.config import MODEL_NAME, TRAINING_DATA_S3_BUCKET

pytestmark = pytest.mark.integration


@pytest.mark.usefixtures("integration_env", "s3_buckets")
def test_full_run_exports_data_and_registers_champion(
    labelled_tickets: int,
    postgres_conn: psycopg.Connection[dict[str, Any]],
    s3_client: Any,
):
    apply_alembic_migrations()

    build_retraining_job(Settings()).run()

    objects = s3_client.list_objects_v2(
        Bucket=TRAINING_DATA_S3_BUCKET, Prefix="training-data/"
    )
    keys = [obj["Key"] for obj in objects.get("Contents", [])]
    assert len(keys) == 1
    assert keys[0].endswith("/train.csv")

    body = s3_client.get_object(Bucket=TRAINING_DATA_S3_BUCKET, Key=keys[0])["Body"]
    lines = body.read().decode("utf-8").strip().splitlines()
    assert len(lines) == labelled_tickets + 1  # header + rows

    with postgres_conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM retraining.classifier_model_registry WHERE model_name = %s",
            (MODEL_NAME,),
        )
        models = cur.fetchall()
    assert len(models) == 1
    assert models[0]["is_champion"] is True
