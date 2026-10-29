# Dependencies
FROM astral/uv:python3.13-bookworm-slim AS dependencies

ENV UV_NO_CACHE=true \
    UV_COMPILE_BYTECODE=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-editable --no-dev

# Runtime
FROM python:3.13-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/src \
    PATH="/opt/venv/bin:$PATH"

COPY --from=dependencies /opt/venv /opt/venv
COPY ./src /src

WORKDIR /src

CMD ["python", "application.py"]
