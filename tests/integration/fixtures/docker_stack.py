from __future__ import annotations

import subprocess  # noqa: S404
import time
import urllib.request
from typing import TYPE_CHECKING

import psycopg
import pytest
import structlog

from tests.integration.config import (
    AWS_ENDPOINT_URL,
    COMPOSE_FILE,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)

if TYPE_CHECKING:
    from collections.abc import Generator

logger = structlog.get_logger(__name__)

STARTUP_TIMEOUT_S = 60


def _compose(*args: str) -> None:
    subprocess.run(  # noqa: S603
        ["docker", "compose", "-f", str(COMPOSE_FILE), *args],  # noqa: S607
        check=True,
    )


def _wait_until_ready() -> None:
    deadline = time.monotonic() + STARTUP_TIMEOUT_S
    while time.monotonic() < deadline:
        try:
            with psycopg.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                dbname=POSTGRES_DB,
                connect_timeout=2,
            ):
                pass
            urllib.request.urlopen(f"{AWS_ENDPOINT_URL}/moto-api/", timeout=2)  # noqa: S310
        except Exception:
            time.sleep(1)
        else:
            return
    raise TimeoutError("Integration stack did not become ready in time")


@pytest.fixture(scope="session")
def docker_stack() -> Generator[None]:
    """Start Postgres + moto for the whole test session and tear them down at the end."""
    logger.info("Starting integration docker-compose stack")
    _compose("up", "-d", "--wait")
    try:
        _wait_until_ready()
        yield
    finally:
        logger.info("Stopping integration docker-compose stack")
        _compose("down", "-v")
