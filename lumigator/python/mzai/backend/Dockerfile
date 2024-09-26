FROM python:3.11-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy the project into the image
ADD . /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app
# RUN uv pip install dist/schemas-0.1.0-py3-none-any.whl
RUN uv sync --frozen

CMD ["uv", "run", "uvicorn", "app.main:app"]