# Backend

## Summary

`backend` represents  the core framework of the Lumigator application,
currently this includes code for the following components:

* API (REST over HTTP)
* Services which allow the API to interact with the rest of the application
* Repositories (for persisting data)
* Repository model representations (data/entities)

## Initialization

To initialize the dependencies and the virtual environment:

```bash
uv sync && \
uv sync --dev && \
source .venv/bin/activate
```

## Data models

As an engineer/contributor, when you change a data model or add a new model which needs to be persisted to the database,
you **MUST** ensure you've consulted and followed the [Alembic README](.alembic/README.md).

## Upgrading

There may be times when changes are required to the database used for persistence.

In order to minimize issues for developers/contributors of Lumigator,
we rely on [alembic](https://alembic.sqlalchemy.org/en/latest/) as a 'dev dependency'.

Breaking changes should be noted in release changelogs, but if you're working on `main` there may be times when you
encounter a database issue that wasn't expected because the schema changed and your local database does not have a
matching schema.

For further information on using Alembic to maintain the correct database schema with the `backend` project,
please see the specific [Alembic README](.alembic/README.md).
