FROM python:3.11-slim-bookworm AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy the project into the image
ADD . /mzai

WORKDIR /mzai/lumigator/python/mzai/backend

FROM base AS main_image

# Sync the project into a new environment, using the frozen lockfile and no dev dependencies
RUN uv sync --no-dev --frozen

CMD ["uv", "run", "--no-dev", "uvicorn",  "--host", "0.0.0.0", "--port", "8000", "backend.main:app"]

FROM base AS dev_image

# Sync the project into a new environment, using the frozen lockfile and no dev dependencies
RUN uv sync --frozen

CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000",  "--reload"]
