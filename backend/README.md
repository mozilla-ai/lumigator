# Platform Backend

## Local setup

(1) Create a virtual environment and install Poetry for managing dependencies.

```
pip install poetry
```

(2) Install requirements.

```
poetry lock && poetry install
```

(3) Run linting checks.

```
make lint
```

(4) Run test suite.

```
make test
```

## Test dependencies

The backend application depends on a handful of external services
(e.g., Postgres, Ray cluster) to function.
These dependencies are configured as pytest fixtures to enable
running unit/integration tests locally while developing.
However, they will not be present if you try to launch the FastAPI server alone via the `main.py` script, 
and the application will fail to start.

To run the entire application locally,
follow the guide in the parent [README.md](../README.md) using Docker Compose.
