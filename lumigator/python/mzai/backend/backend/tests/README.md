# Backend Tests

This folder contains tests for the backend FastAPI application. The types of tests can be broken
down into two distinct categories:

- `unit` tests: Involve isolated functions/classes.
- `integration` tests: Depend on some external service to run.

The external services that the application depends on are the database, Ray cluster, and S3 storage.
Currently, we are using the [`TestContainers`](https://testcontainers-python.readthedocs.io/en/latest/)
library to provide some of these dependencies for testing.

`TestContainers` provides a simple interface for spinning up a Docker container running some service
as part of the testing lifecycle. This is configured in the `conftest.py` file that contains
fixtures for the entire test suite.

## Running Tests

To run the tests, you can use the following command:

```
SQLALCHEMY_DATABASE_URL=sqlite:///local.db uv run pytest
```

## Test Settings

The main settings for the backend application are defined in the `backend.settings.BackendSettings`
class. This class inherits from the
[Pydantic BaseSettings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
class and reads its values from the environment when instantiated. These settings are then used for
instantiating various clients/controlling business logic throughout the application.

The Makefile used to run tests will take the following environment variables from the environment
or the `.env` file (with this file taking precedence) if they exist:

* RAY_WORKER_GPUS (default value `0.0`)
* RAY_WORKER_GPUS_FRACTION (default value `0.0`)
* INFERENCE_PIP_REQS (default value `../jobs/inference/requirements_cpu.txt`)

In cases where a test requires a different dependency than those defined by the `BackendSettings`
class (e.g., for creating a test client for a mock service), a test dependency override can be
pecified in the `conftest.py` fixture.
