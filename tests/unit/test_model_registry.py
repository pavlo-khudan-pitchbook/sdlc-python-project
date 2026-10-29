from unittest.mock import MagicMock

from retraining_job.database.sql import DEMOTE_CHAMPIONS, INSERT_MODEL, PROMOTE_MODEL
from retraining_job.model_registry import ModelRegistry
from retraining_job.sagemaker import TrainingResult


def test_register_returns_model_id(
    mock_db: MagicMock, mock_cursor: MagicMock, completed_training: TrainingResult
):
    mock_cursor.fetchone.return_value = {"model_id": "abc"}

    model_id = ModelRegistry(mock_db).register(
        model_name="ticket-classifier",
        model_version="20260101-020000",
        training=completed_training,
        training_data_s3_uri="s3://bucket/training-data/20260101-020000/",
    )

    assert model_id == "abc"
    assert mock_cursor.execute.call_args.args[0] == INSERT_MODEL


def test_promote_demotes_previous_champion_first(
    mock_db: MagicMock, mock_cursor: MagicMock
):
    ModelRegistry(mock_db).promote("ticket-classifier", "abc")

    executed = [call.args[0] for call in mock_cursor.execute.call_args_list]
    assert executed == [DEMOTE_CHAMPIONS, PROMOTE_MODEL]
