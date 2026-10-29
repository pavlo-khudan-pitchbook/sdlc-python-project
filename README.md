# test-cronjob

Scheduled job that retrains the **support ticket classifier** on SageMaker.

Each execution:
1. Exports human-labelled tickets from Postgres to S3 as a CSV dataset
2. Launches a SageMaker training job on that dataset and waits for it to finish
3. Registers the trained model in the Postgres model registry and promotes it to champion

The job is deployed as a Kubernetes CronJob via the shared `python-cron` Helm chart. The Flux
`HelmRelease` (schedule, env vars, IAM permissions, resources) for dev lives in
[`tf/cron-job.yml`](tf/cron-job.yml).

## Installation
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Install [Docker](https://docs.docker.com/get-docker/)
3. Install dependencies and git hooks:
   ```bash
   uv sync
   uv run pre-commit install
   ```

## Local Development

Local infrastructure (Postgres + moto as a fake S3/SageMaker) runs in Docker Compose. moto
completes training jobs immediately without running the training image.

### 1. Start Local Infrastructure
```bash
docker compose up -d
```

Create the upstream source table and seed a few rows (owned by the Support team in real
environments):
```bash
psql -h localhost -U retraining_user -d retraining -c "
CREATE SCHEMA IF NOT EXISTS support;
CREATE TABLE IF NOT EXISTS support.ticket_labels (
  ticket_id text PRIMARY KEY, subject text NOT NULL, body text NOT NULL,
  customer_email text, category text NOT NULL);
INSERT INTO support.ticket_labels VALUES
  ('T-1','Where is my order?','It has been 10 days','a@example.com','shipping'),
  ('T-2','Refund please','Item arrived broken','b@example.com','refund');"
```

### 2. Run One Execution
Either inside Docker (same as one CronJob execution):
```bash
docker compose --profile job run --rm retraining-job
```

or from the IDE / terminal:
```bash
cp .env.example .env
set -a; source .env; set +a
PYTHONPATH=src uv run src/application.py
```

Buckets are not created by the job. Run `scripts/check_local_sagemaker_integration.py` once
first, or create them manually.

### 3. Verify Outputs
```bash
aws --endpoint-url http://localhost:4566 s3 ls s3://local-training-data/training-data/ --recursive
psql -h localhost -U retraining_user -d retraining \
  -c "SELECT model_version, is_champion, metrics FROM retraining.classifier_model_registry ORDER BY created_at DESC;"
```

### 4. Stop Local Infrastructure
```bash
docker compose down        # keep data
docker compose down -v     # wipe Postgres volume
```

## Scripts

| Script | Purpose |
|---|---|
| `scripts/check_local_sagemaker_integration.py` | Smoke-checks S3 upload + SageMaker training job calls against the local moto stack |

## Testing

```bash
# Unit tests (no Docker required)
uv run pytest tests/unit

# Integration tests (starts its own docker-compose stack)
uv run pytest tests/integration -m integration --no-cov --tb=short
```

See [tests/integration/README.md](tests/integration/README.md) for details.

## CI/CD

GitLab CI (`.gitlab-ci.yml`) builds on the shared `python-cron` template. On every pipeline:
lint → unit tests → Docker image → deploy to dev and preprod. The prod deploy is manual.

## Deployment

`tf/cron-job.yml` holds the Flux resources for the dev cluster:

| Resource | Purpose |
|---|---|
| `ImageRepository` | Watches the ECR repository for new image tags |
| `ImagePolicy` | Picks the newest `vX.Y.Z-dev` tag and updates the image line marked `$imagepolicy` |
| `HelmRelease` | Deploys the shared `python-cron` chart: schedule, env vars, resources, IAM permissions |

To change the schedule or pause the job, edit `cronjobs[].schedule` / `suspend` in the
`HelmRelease`.

## Configuration

All configuration comes from environment variables, see `src/retraining_job/settings.py` and
`.env.example`.
