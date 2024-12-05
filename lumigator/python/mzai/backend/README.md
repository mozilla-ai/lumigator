# Backend

`backend` represents the core framework of the Lumigator application. Currently, it includes code
for the following components:

* API (REST over HTTP).
* Services which allow the API to interact with the rest of the application.
* Repositories (for persisting data).
* Repository model representations (data/entities).

## Initialization

To initialize the dependencies and the virtual environment:

```bash
uv sync && \
uv sync --dev && \
source .venv/bin/activate
```

## Test instructions

The backend includes both unit tests (requiring no additional containers) and integration tests (currently requiring a live Ray instance in the same network where the application and tests are running, and test LocalStack containers also in the same configuration).

The backend needs to retrieve the location of the database used in tests via the `SQLALCHEMY_DATABASE_URL` enviroment variable. For simplicity, SQLite is used inside the test container. To run the tests, please use:

```bash
SQLALCHEMY_DATABASE_URL=sqlite:///local.db uv run pytest
```

Note that this will create an SQLite database file named `local.db` in the `backend` directory. Remove it before running another batch of tests.

The tests include a unit test suite and an integration test suite. There are make targets available at the root folder, as follows:

* `backend-test`: runs `backend-unit-test` and `backend-int-test`
  * `backend-unit-test`: runs tests in `backend/tests/unit/*/test_*.py` (any depth of subfolders)
  * `backend-int-test`: runs tests in `backend/tests/int/*/test_*.py` (any depth of subfolders)

The SQLite configuration making use of a local file is used in both unit and integration tests. Test containers are needed for integration tests. Fake or mock services are used in unit tests, usually via the [`requests-mock`](https://pypi.org/project/requests-mock/) package in the case of HTTP APIs. Specifically, the S3 file system driver is replaced with an [in-memory implementation](https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec.implementations.memory.MemoryFileSystem) of the `AbstractFileSystem` interface via [registry modification](https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec.registry.register_implementation).

## Data models

As an engineer/contributor, when you change a data model or add a new model which needs to be
persisted to the database, you **MUST** ensure you've consulted and followed the
[Alembic operational guide](https://mozilla-ai.github.io/lumigator).

## Database Upgrade

There may be times when changes are required to the database used for persistence. To minimize
issues for developers/contributors of Lumigator, we rely on
[alembic](https://alembic.sqlalchemy.org/en/latest/) as a 'dev dependency'.

Breaking changes should be noted in release changelogs, but if you're working on `main` there may be
times when you encounter a database issue that wasn't expected because the schema changed and your
local database does not have a matching one.

For further information on using Alembic to maintain the correct database schema with the `backend`
project, please see the specific
[Alembic operational guide](https://mozilla-ai.github.io/lumigator).
