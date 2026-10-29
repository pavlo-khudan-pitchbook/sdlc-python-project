"""
Integration Test Fixtures.

- Docker compose stack management (Postgres + moto for S3/SageMaker)
- Source table seeding
- AWS clients pointed at moto
"""

# flake8: noqa: F403

from __future__ import annotations

import pytest

from tests.integration.config import get_integration_env_vars
from tests.integration.fixtures.aws import *
from tests.integration.fixtures.docker_stack import *
from tests.integration.fixtures.postgres_db import *


@pytest.fixture
def integration_env(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Point Settings() at the integration stack."""
    env = get_integration_env_vars()
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return env
