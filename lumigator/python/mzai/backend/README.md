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

The backend needs to retrieve the location of the database used in tests via the `SQLALCHEMY_DATABASE_URL` enviroment variable. For simplicity, SQLite is used inside the test container. To run the tests, please use:

```bash
SQLALCHEMY_DATABASE_URL=sqlite:///local.db uv run pytest
```

Note that this will create an SQLite database file named `local.db` in the `backend` directory. Remove it before running another batch of tests.

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
