FROM python:3.11-slim-bookworm AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy the project into the image
ADD . /mzai

WORKDIR /mzai/lumigator/backend
ENV PYTHONPATH=/mzai/lumigator/backend:/mzai/lumigator/jobs

FROM base AS main_image

# Sync the project into a new environment, using the frozen lockfile and no dev dependencies
RUN uv sync --no-dev --frozen

CMD ["uv", "run", "--no-dev", "uvicorn",  "--host", "0.0.0.0", "--port", "8000", "backend.main:app"]

FROM base AS dev_image

# Sync the project into a new environment, using the frozen lockfile and all dependencies
RUN uv sync --frozen


CMD [\
    "uv","run", "-m", "debugpy", "--listen", "0.0.0.0:5678", \
    "-m", "uvicorn", "backend.main:app", "--reload", \
    "--reload-dir", "/mzai/lumigator/jobs", \
    "--reload-dir", "/mzai/lumigator/schemas", \
    "--host", "0.0.0.0", \
    "--port", "8000" \
]
