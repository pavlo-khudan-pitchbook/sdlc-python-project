from __future__ import annotations

from typing import TYPE_CHECKING, Any

import psycopg
import pytest
from psycopg.rows import dict_row

from tests.integration.config import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)

if TYPE_CHECKING:
    from collections.abc import Generator

SAMPLE_TICKETS = [
    ("T-1", "Where is my order?", "It has been 10 days", "a@example.com", "shipping"),
    ("T-2", "Refund please", "Item arrived broken", "b@example.com", "refund"),
    ("T-3", "Change address", "I moved last week", "c@example.com", "account"),
    ("T-4", "Late delivery", "Still waiting for parcel", "d@example.com", "shipping"),
]


@pytest.fixture
def postgres_conn(docker_stack: None) -> Generator[psycopg.Connection[dict[str, Any]]]:
    with psycopg.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
        row_factory=dict_row,
        autocommit=True,
    ) as conn:
        yield conn


@pytest.fixture
def labelled_tickets(postgres_conn: psycopg.Connection[dict[str, Any]]) -> Generator[int]:
    """Create the upstream source table (owned by the Support team in real envs) and seed it."""
    with postgres_conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS support")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS support.ticket_labels (
                ticket_id text PRIMARY KEY,
                subject text NOT NULL,
                body text NOT NULL,
                customer_email text,
                category text NOT NULL
            )
            """
        )
        cur.executemany(
            "INSERT INTO support.ticket_labels VALUES (%s, %s, %s, %s, %s)",
            SAMPLE_TICKETS,
        )
    yield len(SAMPLE_TICKETS)
    with postgres_conn.cursor() as cur:
        cur.execute("DROP SCHEMA support CASCADE")
        cur.execute("DROP SCHEMA IF EXISTS retraining CASCADE")
        cur.execute("DROP TABLE IF EXISTS public.alembic_version")
