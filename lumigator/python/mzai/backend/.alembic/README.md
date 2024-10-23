# Using Alembic with Lumigator

https://alembic.sqlalchemy.org/en/latest/index.html

> [Alembic](https://alembic.sqlalchemy.org/) is a lightweight database migration tool for usage with the
> [SQLAlchemy](https://www.sqlalchemy.org/) Database Toolkit for Python.

In Lumigator, whenever we make changes to the database (DB) schemas (via our SQLAlchemy models),
we can create a migration path for the DB, removing blockers for developers working on the codebase.

In future this should be extended to form part of releases so that moving between versions of Lumigator is easy,
even when the database schemas have breaking changes.

This document covers the ways in which Alembic can be used.

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

## Viewing migration history

`alembic history`

## Show your current revision

`alembic current`

## Upgrading

Upgrade your database to match the latest models:

`alembic upgrade head`

You can also upgrade 'relative' to your current state, so to move forwards 1 revision:

`alembic upgrade +1`

If you know the version you want to migrate to, you can specify it:

`alembic upgrade cb3cf47d9259`

## Downgrading

To downgrade to the original state (not really recommended) use:

`alembic downgrade base`

You can also downgrade 'relative' to your current state, so to move backwards 1 revision:

`alembic downgrade -1`

If you know the version you want to migrate to, you can specify it:

`alembic downgrade If you know the version you want to migrate to, you can specify it:

`alembic upgrade cb3cf47d9259``

## Creating revisions

When you make a change to a database schema via the models, you should create a migration (revision) that handles
upgrading the database, and downgrading too (this allows a linear chain to be followed when moving between migrations).

### Manual revision

To create an empty revision that you populate manually:

`alembic revision -m "{Explanatory commit-like message}"`

This will create a new file under `versions/`.

For example:

```bash
alembic revision -m "create db"
```

We should see a new Python file created with a commit/ID prepended to your message:

`cb3cf47d9259_create_db.py`

### Automatic* revision

Alembic can attempt to work out the changes required to migrate your database if you ask it to create a revision using
the `--autogenerate` flag when creating a revision.

`alembic revision --autogenerate -m {Explanatory commit-like message}`

Please note that 'automatic' doesn't mean this can be completely automated, as manual steps are still required in
verifying the output.

### Revision structure

The main parts of the migration Python files Alembic creates are:

| Name            | Purpose                                                                      |
|-----------------|------------------------------------------------------------------------------|
| `revision`      | ID of this migration                                                         |
| `down_revision` | ID of the previous revision (`None` when this is the first migration)        |
| `upgrade()`     | Function which handles changes required when upgrading to this migration     |
| `downgrade()`   | Function which handles changes required when downgrading from this migration |
