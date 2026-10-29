# Integration Testing

Black-box integration tests for the retraining cronjob, run against real infrastructure
dependencies deployed locally via containers:

- **PostgreSQL**: source of labelled tickets and the model registry
- **moto server**: fake AWS S3 and SageMaker

The docker-compose stack (`tests/integration/docker-compose.yml`) is started and stopped by
the `docker_stack` session fixture. Ports differ from the root `docker-compose.yml`, so both
stacks can run at the same time.

## Prerequisites

- Docker and Docker Compose
- Python 3.13+
- uv (package manager)

## Quick Start

```bash
uv run pytest tests/integration -m integration --no-cov --tb=short
```

## Test Categories

### Full run (`test_retraining_run.py`)
- Labelled tickets are exported to S3 as `training-data/<run_id>/train.csv`
- A SageMaker training job is started (moto completes it immediately)
- The model is registered and flagged as champion

### Fail fast (`test_fail_fast.py`)
- Migrations fail when Postgres is unreachable

## Known limitations

- moto does not execute the training container, so model quality and SageMaker metrics are not
  exercised here.
