# Backend Tests

This folder contains tests for the backend FastAPI application. The types of tests can be broken
down into two distinct categories:

- `unit` tests: Involve isolated functions/classes.
- `integration` tests: Depend on some external service to run.


We currently test unit and integration tests via the `Makefile`:
- `test-sdk`
- `test-backend`
- `test-jobs-unit`

## Running Individual Tests
To run individual tests, you can change the pytest path by specifying the `-k` flag in pytest, which runs tests [based on string expression](https://docs.pytest.org/en/6.2.x/usage.html#specifying-tests-selecting-tests)

```uv run $(DEBUGPY_ARGS) -m pytest -s -o \
	python_files="backend/tests/integration/*/test_*.py" \
	-k 'test_full_experiment_launch'
```

As an example, editing this runs only the `test_full_experiment_launch` method in `test-backend-integration`
```sh
test-backend-integration:
	cd lumigator/python/mzai/backend/; \
	docker container list --all; \
	S3_BUCKET=lumigator-storage \
	RAY_HEAD_NODE_HOST=localhost \
	RAY_DASHBOARD_PORT=8265 \
	SQLALCHEMY_DATABASE_URL=sqlite:////tmp/local.db \
	RAY_WORKER_GPUS="0.0" \
	RAY_WORKER_GPUS_FRACTION="0.0" \
	INFERENCE_PIP_REQS=../jobs/inference/requirements_cpu.txt \
	INFERENCE_WORK_DIR=../jobs/inference \
	EVALUATOR_PIP_REQS=../jobs/evaluator/requirements.txt \
	EVALUATOR_WORK_DIR=../jobs/evaluator \
	EVALUATOR_LITE_PIP_REQS=../jobs/evaluator_lite/requirements.txt \
	EVALUATOR_LITE_WORK_DIR=../jobs/evaluator_lite \
	PYTHONPATH=../jobs:$$PYTHONPATH \
	uv run $(DEBUGPY_ARGS) -m pytest -s -o \
	python_files="backend/tests/integration/*/test_*.py" \
	-k 'test_full_experiment_launch'
```

Additionally, you can run this directly on the commandline so as to not change the Makefile.

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
- test-backend # runs both
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
