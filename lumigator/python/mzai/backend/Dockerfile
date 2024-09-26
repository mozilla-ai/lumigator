FROM python:3.11-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy the project into the image
ADD . /app

WORKDIR /app

COPY --from=lumi-schemas:1 /app/dist dist 

# Override schemas editable source and change to built wheel
# TODO Change from static file name
RUN uv add schemas dist/schemas-0.1.0-py3-none-any.whl

# Sync the project into a new environment, using the frozen lockfile
RUN uv sync --frozen

CMD ["uv", "run", "uvicorn", "app.main:app"]