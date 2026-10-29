from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from structlog import get_logger

from retraining_job.database.sql import SELECT_LABELLED_TICKETS
from retraining_job.metrics import EXPORTED_ROWS

if TYPE_CHECKING:
    from retraining_job.database import PostgresDB

logger = get_logger()

CSV_COLUMNS = ["ticket_id", "subject", "body", "customer_email", "category"]


@dataclass(frozen=True)
class ExportResult:
    s3_uri: str  # S3 prefix, consumed as a SageMaker training channel
    row_count: int


class TrainingDataExporter:
    """Exports human-labelled support tickets from Postgres to S3 as a CSV dataset."""

    def __init__(
        self,
        db: PostgresDB,
        s3_client: Any,
        bucket: str,
        source_table: str,
    ):
        self._db = db
        self._s3 = s3_client
        self._bucket = bucket
        self._source_table = source_table

    def export(self, run_id: str) -> ExportResult:
        rows = self._fetch_rows()

        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

        prefix = f"training-data/{run_id}/"
        self._s3.put_object(
            Bucket=self._bucket,
            Key=f"{prefix}train.csv",
            Body=buffer.getvalue().encode("utf-8"),
        )

        EXPORTED_ROWS.set(len(rows))
        s3_uri = f"s3://{self._bucket}/{prefix}"
        logger.info(f"Exported {len(rows)} labelled tickets to {s3_uri}")
        return ExportResult(s3_uri=s3_uri, row_count=len(rows))

    def _fetch_rows(self) -> list[dict[str, Any]]:
        query = SELECT_LABELLED_TICKETS.format(table=self._source_table)
        with self._db.connection() as conn, conn.cursor() as cur:
            cur.execute(query)  # type: ignore[arg-type]
            return cur.fetchall()
