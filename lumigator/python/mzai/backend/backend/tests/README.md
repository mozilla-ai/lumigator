# Backend Tests

This folder contains tests for the backend FastAPI application.
The types of tests can be broken down into two distinct categories:
- `unit` tests that involve isolated functions/classes, and
- `integration` tests that depend on some external service to run

The external services that the application depends on are
the Postgres database, Ray cluster, and S3 storage.

Currently, we are using the [TestContainers](https://testcontainers-python.readthedocs.io/en/latest/)
library to provide some of these dependencies for testing.
TestContainers provides a simple interface for spinning up a Docker container running some service
as part of the testing lifecycle.This is configured in the `conftest.py` file
that contains fixtures for the entire test suite.

## Running Tests

```
SQLALCHEMY_DATABASE_URL=sqlite:///local.db uv run pytest
```

## Test Settings

The main settings for the backend application are defined in the
`backend.settings.BackendSettings` class.
This class inherits from the
[Pydantic BaseSettings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
class and reads its values from the envrionment when instantiated.
These settings are then used for instantiating various clients/controlling business logic
throughout the application.

In cases where a test requires a different dependency than defined by the `BackendSettings` class
(e.g., for constructing a test client for some faked out service),
a test dependency override can be specified in the `conftest.py` fixture.

### Global Dependency Injection
## TODO: Resolve

Currently a global instance of this class is defined in the `backend.settings.settings` variable
and imported throughout the application. This means that settings are read for the environment
one time as soon as the settings class is imported.
This means that settings for the TestContainers services that are defined in the `conftest.py` fixtures
cannot be injected into the `BackendSettings`
because they only become available after the environment variables are read.

An option to look into is refactoring the application to read the `BackendSettings`
dynamically, instead of by accessing a global variable,
so that env vars can be injected into the settings for testing after the fixtures are initialized.

Reerence: https://fastapi.tiangolo.com/advanced/settings/#settings-in-a-dependency
