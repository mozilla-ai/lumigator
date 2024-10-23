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

## Upgrading

There may be times when changes are required to the database used for persistence.

In order to minimize issues for developers/contributors of Lumigator,
we rely on [alembic](https://alembic.sqlalchemy.org/en/latest/) as a 'dev dependency'.

Alembic facilitates migrations of our database schemas.

Breaking changes should be noted in release changelogs, but if you're working on `main` there may be times when you
encounter a database issue that wasn't expected because the schema changed and your local database does not have a
matching schema.

For further information on using Alembic with the `backend` project,
please see the specific [README](.alembic/README.md).
