# App stage
FROM python:3.10.13 as setup

WORKDIR /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/

RUN poetry install --no-root --without dev

ENV PYTHONPATH=/app/src

COPY ./src /app/src

FROM setup as app

ENTRYPOINT ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]

# Testing stage
FROM setup as testing

RUN poetry install --no-root

COPY ./scripts /app/scripts
