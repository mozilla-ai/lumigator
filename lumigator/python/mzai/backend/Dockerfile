FROM python:3.11-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy the project into the image
ADD . /app

WORKDIR /app

COPY --from=lumi-schemas:1 /app/dist dist 

# Sync the project into a new environment, using the frozen lockfile
RUN uv sync --frozen

CMD ["uv", "run", "uvicorn", "app.main:app"]