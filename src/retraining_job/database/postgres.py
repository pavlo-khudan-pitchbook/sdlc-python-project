from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

import psycopg
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row
from structlog import get_logger

if TYPE_CHECKING:
    from collections.abc import Iterator

logger = get_logger()


class PostgresDB:
    """Thin psycopg wrapper.

    The job is short-lived, so a new connection is opened per unit of work instead of
    keeping a connection pool around.
    """

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        dbname: str,
        connect_timeout: int = 10,
    ):
        if not host or not password:
            raise ValueError(
                "Database host/password must be provided (DB_HOST, DB_PASSWORD)"
            )

        self.dbname = dbname
        self.conninfo = make_conninfo(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname,
            connect_timeout=connect_timeout,
        )

    @contextmanager
    def connection(self) -> Iterator[psycopg.Connection[dict[str, Any]]]:
        """Yield a connection; commits on success, rolls back on error."""
        logger.debug(f"Opening Postgres connection dbname={self.dbname}")
        with psycopg.connect(self.conninfo, row_factory=dict_row) as conn:
            yield conn
