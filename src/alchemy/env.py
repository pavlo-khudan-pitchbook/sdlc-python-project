from alembic import context
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import URL
from structlog import get_logger

from alchemy import models
from retraining_job.settings import Settings

logger = get_logger()

settings = Settings()
config = context.config
target_metadata = models.metadata


def _db_url() -> URL:
    return URL.create(
        drivername="postgresql+psycopg",
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )


def run_migrations_offline() -> None:
    context.configure(
        url=_db_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        _db_url(),
        poolclass=pool.NullPool,
        connect_args={"connect_timeout": settings.db_connect_timeout},
    )

    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                include_schemas=True,
            )

            with context.begin_transaction():
                context.run_migrations()
    except Exception as e:
        logger.error(f"Failed to complete Alembic Migration. Error: {e!s}")
        raise


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
