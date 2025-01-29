# Backend Tests

This folder contains tests for the backend FastAPI application. The types of tests can be broken
down into two distinct categories:

- `unit` tests: Involve isolated functions/classes.
- `integration` tests: Depend on some external service to run.
-
We currently test unit and integration tests via the `Makefile`:
- `test-sdk`
- `test-backend`
- `test-jobs-unit`

The external services that the application depends on are the database, Ray cluster, and S3-compatible storage.

## Test Dependencies

The backend tests offer two sets of service dependencies as fixtures:

* `dependency_overrides_fakes`, to be used in unit tests, mocks all external services.
* `dependency_overrides_services`, to be used in integration tests, provides real clients for external services (except the DB).

By default, an embedded SQLite database is used in both cases.

## Running Tests

To run the backend tests, you can use the configured commands in the Makefile:

```
- make test-backend-integration
- make test-backend-unit
- test-backend
```

## Test Settings

The main settings for the backend application are defined in the `backend.settings.BackendSettings`
class. This class inherits from the
[Pydantic BaseSettings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
class and reads its values from the environment when instantiated. These settings are then used for
instantiating various clients/controlling business logic throughout the application.

In cases where a test requires a different dependency than those defined by the `BackendSettings`
class (e.g., for creating a test client for a mock service), a test dependency override can be
pecified in the `conftest.py` fixture.
