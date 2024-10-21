FROM python:3.11-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy the project into the image
ADD . /mzai

WORKDIR /mzai/lumigator/python/mzai/backend AS main_image

# Sync the project into a new environment, using the frozen lockfile and no dev dependencies
RUN uv sync --frozen --no-dev

CMD ["uv", "run", "uvicorn",  "--host", "0.0.0.0", "--port", "8000", "backend.main:app"]




FROM main_image AS dev_image

# Sync the project into a new environment, using the frozen lockfile
RUN uv sync --frozen

CMD ["uv", "run", "uvicorn",  "--host", "0.0.0.0", "--port", "8000", "backend.main:app"]