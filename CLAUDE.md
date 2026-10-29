# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

**test-cronjob** is a short-lived Python job, run on a schedule as a Kubernetes CronJob, that
retrains the support ticket classifier.

```
application.py
    ↓ apply Alembic migrations
    ↓ build dependencies (configuration.py)
RetrainingJob.run()
    ├→ TrainingDataExporter   Postgres (support.ticket_labels) → S3 CSV
    ├→ SageMakerTrainer       create_training_job + poll until terminal state
    └→ ModelRegistry          insert into retraining.classifier_model_registry, promote champion
```

- `configuration.py` is the composition root; classes receive dependencies via constructors
- `src/alchemy/` holds the SQLAlchemy models and Alembic migrations for the `retraining` schema
- The `support.ticket_labels` table is owned upstream; this repo only reads it
- `tf/cron-job.yml` is the Flux `HelmRelease` (shared `python-cron` chart) with the schedule,
  env vars and IAM permissions; CI only builds and pushes the image

## Common Development Commands

```bash
uv sync                                   # install deps
uv run pre-commit install                 # git hooks (required)
docker compose up -d                      # local Postgres + moto
docker compose --profile job run --rm retraining-job   # one job execution
uv run pytest tests/unit                  # unit tests
uv run pytest tests/integration -m integration --no-cov   # integration tests
uv run pre-commit run --all-files         # lint + type check
```

### Scripts Convention

Scripts must not import or depend on the job's `Settings()` class. Hardcode configuration values
to target the local stack, so scripts stay self-contained.

### Database Migrations

```bash
cd src/alchemy
uv run alembic revision --autogenerate -m "description"
```

- All schema changes via Alembic migrations
- Applied automatically at job start via `apply_alembic_migrations()`
- Test the migration both up and down before committing
