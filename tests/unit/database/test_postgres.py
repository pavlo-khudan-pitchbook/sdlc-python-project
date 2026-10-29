import pytest

from retraining_job.database import PostgresDB


def test_missing_password_raises():
    with pytest.raises(ValueError, match="host/password"):
        PostgresDB(host="localhost", port=5432, user="u", password="", dbname="db")


def test_conninfo_contains_connection_params():
    db = PostgresDB(host="db.local", port=5433, user="u", password="p", dbname="db")  # noqa: S106

    assert "host=db.local" in db.conninfo
    assert "port=5433" in db.conninfo
