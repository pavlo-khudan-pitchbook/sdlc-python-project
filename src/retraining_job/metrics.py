from prometheus_client import Counter, Gauge, Histogram

TRAINING_RUNS = Counter(
    "retraining_job_training_runs_total",
    "Number of retraining runs by final SageMaker training job status",
    ["status"],
)

EXPORTED_ROWS = Gauge(
    "retraining_job_exported_rows",
    "Number of labelled tickets exported for the latest training run",
)

JOB_DURATION_SECONDS = Histogram(
    "retraining_job_duration_seconds",
    "End-to-end duration of a retraining run",
    buckets=(60, 300, 900, 1800, 3600, 7200),
)
