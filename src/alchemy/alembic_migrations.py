from pathlib import Path

from alembic import command
from alembic.config import Config
from structlog import get_logger

logger = get_logger(__name__)

dir_path = Path(__file__).parent


def apply_alembic_migrations() -> None:
    logger.info("Migration processing started")
    try:
        alembic_cfg = Config(dir_path / "alembic.ini")
        alembic_cfg.set_main_option("script_location", str(dir_path))
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        logger.error(f"Failed to run `apply_alembic_migrations`. Error: {e!s}")
        raise

    logger.info("Successfully finished Migration processing")
