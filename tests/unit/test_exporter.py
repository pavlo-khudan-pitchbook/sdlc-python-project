from unittest.mock import MagicMock

from retraining_job.exporter import TrainingDataExporter


def test_export_writes_csv_to_run_prefix(mock_db: MagicMock, mock_cursor: MagicMock):
    mock_cursor.fetchall.return_value = [
        {
            "ticket_id": "T-1",
            "subject": "Where is my order?",
            "body": "It has been 10 days",
            "customer_email": "a@example.com",
            "category": "shipping",
        }
    ]
    s3_client = MagicMock()
    exporter = TrainingDataExporter(
        db=mock_db,
        s3_client=s3_client,
        bucket="test-training-data",
        source_table="support.ticket_labels",
    )

    result = exporter.export("20260101-020000")

    assert result.row_count == 1
    assert result.s3_uri == "s3://test-training-data/training-data/20260101-020000/"
    put_kwargs = s3_client.put_object.call_args.kwargs
    assert put_kwargs["Key"] == "training-data/20260101-020000/train.csv"
    assert put_kwargs["Body"].decode("utf-8").startswith("ticket_id,subject,body")
