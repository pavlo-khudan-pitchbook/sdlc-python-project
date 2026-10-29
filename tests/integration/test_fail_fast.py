from __future__ import annotations

import pytest
from sqlalchemy.exc import OperationalError

from alchemy.alembic_migrations import apply_alembic_migrations

pytestmark = pytest.mark.integration


@pytest.mark.usefixtures("docker_stack", "integration_env")
def test_migrations_fail_when_postgres_is_unreachable(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DB_PORT", "1")
    monkeypatch.setenv("DB_CONNECT_TIMEOUT", "1")

    with pytest.raises(OperationalError):
        apply_alembic_migrations()
