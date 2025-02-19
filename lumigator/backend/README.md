# Backend

`backend` represents the core framework of the Lumigator application. Currently, it includes code
for the following components:

* API (REST over HTTP).
* Services which allow the API to interact with the rest of the application.
* Repositories (for persisting data).
* Repository model representations (data/entities).

## Initialization

This application uses `uv` as a package manager, you can follow the [installation instructions](https://docs.astral.sh/uv/getting-started/installation/) to install it

To initialize the dependencies and the virtual environment:

```bash
uv sync && \
uv sync --dev && \
source .venv/bin/activate
```

## Make usage

The available Makefile contains targets to:

- start the system using docker compose (e.g. `local-up`, `start-lumigator`, `start-lumigator-build`)
- stop the system (e.g. `local-down`, `stop-lumigator`)
- run tests (e.g `test-backend`, `test-sdk`, `test-all`)

When the system is started for the first time, a `.env` file is created from the existing
`.env.template`. This file contains different parameters passed to the system as environment
variables and you can customize it to suit your specific use case.

> [!NOTE]
> We are mindful about your personal settings so we will never overwrite them. For this reason,
> if you are pulling a new version of lumigator from the repo please make sure that your `.env`
> file is consistent with the latest `.env.template`, minus your parameters.
Alternatively, if it does not contain any hardcoded settings of your own, delete the .env and Lumigator will create a new one.

## Test instructions

The backend includes both unit tests (requiring no additional containers) and integration
tests (currently requiring a live Ray instance in the same network where the application
and tests are running). Fake or mock services are used in unit tests, usually via the
[`requests-mock`](https://pypi.org/project/requests-mock/) package in the case of HTTP APIs.
Specifically, the S3 file system driver is replaced with an [in-memory implementation](https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec.implementations.memory.MemoryFileSystem)
of the `AbstractFileSystem` interface via [registry modification](https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec.registry.register_implementation).

The following make targets are available for tests:

- `test-sdk-unit`, `test-sdk-integration` run, respectively, unit and integration tests on the sdk.
`test-sdk` runs both, first making sure that containers are available to run the integration tests
and starting them if not

- `test-backend-unit`, `test-backend-integration` run, respectively, unit and integration tests on the backend.
`test-backend` runs both, first making sure that containers are available to run the integration tests
and starting them if not

- `test-jobs-unit` runs unit tests on individual jobs. Currently we have two sub-targets for this,
`test-jobs-inference-unit` and `test-jobs-evaluation-unit`.

- `test-all` runs all the tests together

## Data models and database upgrades

There may be times when changes are required to the database we use to persist dataset and
experiment metadata. To minimize issues for developers/contributors of Lumigator, we rely on
[alembic](https://alembic.sqlalchemy.org/en/latest/) as a 'dev dependency'.

Breaking changes should be noted in release changelogs, but if you're working on `main` there may be
times when you encounter a database issue that wasn't expected because the schema changed and your
local database does not have a matching one.

As an engineer/contributor, when you change a data model or add a new model which needs to be
persisted to the database, you **MUST** ensure you've consulted and followed the
[Alembic operational guide](https://mozilla-ai.github.io/lumigator/operations-guide/alembic.html).
