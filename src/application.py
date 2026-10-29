from structlog import get_logger

from alchemy.alembic_migrations import apply_alembic_migrations
from configuration import build_retraining_job, setup_logging
from retraining_job.settings import Settings

logger = get_logger()


def main() -> None:
    settings = Settings()
    setup_logging(settings.log_level, settings.log_format)
    logger.info(f"Starting retraining job environment={settings.environment}")

    apply_alembic_migrations()
    job = build_retraining_job(settings)

    try:
        job.run()
    except Exception as e:
        logger.error(f"Retraining job failed. Error: {e!s}")

    logger.info("Retraining job finished")


if __name__ == "__main__":
    main()
