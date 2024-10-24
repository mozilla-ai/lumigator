# Using Alembic with Lumigator

https://alembic.sqlalchemy.org/en/latest/index.html

> [Alembic](https://alembic.sqlalchemy.org/) is a lightweight database migration tool for usage with the
> [SQLAlchemy](https://www.sqlalchemy.org/) Database Toolkit for Python.

In Lumigator, whenever we make changes to the database (DB) schemas (via our SQLAlchemy models),
we can create a migration path for the DB, removing blockers for developers working on the codebase.

In future this should be extended to form part of releases so that moving between versions of Lumigator is easy,
even when the database schemas have breaking changes.

This document covers the ways in which Alembic can be used.

**NOTE**: Alembic creates an additional table in the database which it uses to store the matching revision ID.

## Data model changes

When code changes are made to the data models, or when new models are added, a manual step is
required in order to ensure that the models are visible to Alembic.

The imports at the top of [env.py](env.py) **MUST** import your package:

`from backend.records.{package} import * # noqa: F403`

The reason the wildcard is used is so you don't have to explicitly import *every* type in the package,
which makes this solution more brittle. The comment is required to ignore the
[Flake8 F403](https://www.flake8rules.com/rules/F403.html) rule which causes issues with `ruff` linting.

This ensures that the types are loaded such that the `BaseRecord.metadata` fully represents all our types to Alembic.

If a package is not imported then changes will not be captured by Alembic and shown in migration revisions.

## Environment variables

In order to connect to a 'real' database to compare against the models, an `SQLALCHEMY_DATABASE_URL` is required to be
present in your environment.

You can `export` the variable in your shell, or provide it on each invocation.

e.g.

```bash
export SQLALCHEMY_DATABASE_URL=sqlite:///local.db
```

```bash
SQLALCHEMY_DATABASE_URL=sqlite:///local.db alembic history
```

Examples shown in this document will presume `SQLALCHEMY_DATABASE_URL` is exported.

If `SQLALCHEMY_DATABASE_URL` is not present then a default of `sqlite:///local.db` will be used (see: `alembic.ini`)

If you've followed the `README` for `backend` then you will have sourced the virtual environment which means you can
run the `alembic` command directly in the terminal, but you can also run it using `uv`:

```bash
uv run alembic --version
```

## Alembic commands

### Viewing migration history

```bash
alembic history
```

### Show your current revision

```bash
alembic current
```

### Upgrading

Upgrade your database to match the latest models:

```bash
alembic upgrade head
```

You can also upgrade 'relative' to your current state, so to move forwards 1 revision:

```bash
alembic upgrade +1
```

If you know the version you want to migrate to, you can specify it:

```bash
alembic upgrade cb3cf47d9259
```

### Downgrading

To downgrade to the original state (not really recommended) use:

```bash
alembic downgrade base
```

You can also downgrade 'relative' to your current state, so to move backwards 1 revision:

```bash
alembic downgrade -1
```

If you know the version you want to migrate to, you can specify it:

```bash
alembic upgrade cb3cf47d9259
````

### Creating revisions

When you make a change to a database schema via the models, you should create a migration (revision) that handles
upgrading the database, and downgrading too (this allows a linear chain to be followed when moving between migrations).

#### Manual revision

To create an empty revision that you populate manually:

```bash
alembic revision -m "{Explanatory commit-like message}"
```

This will create a new file under `versions/`.

For example:

```bash
alembic revision -m "create db"
```

We should see a new Python file created with a commit/ID prepended to your message:

`cb3cf47d9259_create_db.py`

#### Automatic* revision

Alembic can attempt to work out the changes required to migrate your database if you ask it to create a revision using
the `--autogenerate` flag when creating a revision.

```bash
alembic revision --autogenerate -m {Explanatory commit-like message}
```

Please note that 'automatic' doesn't mean this can be completely automated, as manual steps are still required in
verifying the output.

#### Revision structure

The main parts of the migration Python files Alembic creates are:

| Name            | Purpose                                                                      |
|-----------------|------------------------------------------------------------------------------|
| `revision`      | ID of this migration                                                         |
| `down_revision` | ID of the previous revision (`None` when this is the first migration)        |
| `upgrade()`     | Function which handles changes required when upgrading to this migration     |
| `downgrade()`   | Function which handles changes required when downgrading from this migration |
