# Using Alembic with Lumigator

From: https://alembic.sqlalchemy.org/en/latest/index.html

> [Alembic](https://alembic.sqlalchemy.org/) is a lightweight database migration tool for usage with the
> [SQLAlchemy](https://www.sqlalchemy.org/) Database Toolkit for Python.

In Lumigator, whenever we make changes to the database (DB) schemas (via our SQLAlchemy models),
we must create a migration path for the DB, removing blockers for developers working on the codebase, and operators
upgrading to newer versions of Lumigator.

For new installations of Lumigator, Alembic is enabled by default to create the database and manage migrations.

This document covers the ways in which Alembic can be used with Lumigator.

**NOTE**: Alembic creates an additional table (`alembic_version`) in the database which it uses to store the matching
revision ID.

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

In order to connect to a 'real' database to compare its state against the codified data models, an
`SQLALCHEMY_DATABASE_URL` is required to be present in your environment.

You can `export` the variable in your shell, or provide it on each invocation of `alembic`:

```bash
export SQLALCHEMY_DATABASE_URL=sqlite:///local.db
```

```bash
SQLALCHEMY_DATABASE_URL=sqlite:///local.db alembic history
```

Examples shown in this document assume `SQLALCHEMY_DATABASE_URL` is exported.

If `SQLALCHEMY_DATABASE_URL` is not present then a default of `sqlite:///local.db` will be used (see: `alembic.ini`:
`sqlalchemy.url ` setting).

If you've followed the `README` for `backend` then you will have sourced the virtual environment which means you can
run the `alembic` command directly in the terminal, but you can also run it using `uv`:

```bash
uv run alembic --version
```

## Alembic commands

### Pre-existing databases (not currently managed by Alembic)

Existing Lumigator operators/contributors may already have a populated database with data they don't want to lose.

In this scenario, the database must be brought under the management of Alembic using the alembic `stamp` command.

This is done by stamping the database to indicate the version of revisions that Alembic should manage 'from' going
forward.

#### My database is up to date

If you believe your database already matches the most up-to-date models:

```bash
alembic stamp head
```

#### My database is in a different state (from a prior release)

This scenario requires manual review of the existing revisions stored in the [versions folder](versions/),
in order to determine which revision ID represents the current state of the database containing the data.

Revisions are stored in a format resembling a linked-list, with each revision containing a `revision` ID and
`down_revision` ID (which can be `None` for the initial revision). In each revision the changes captured in the
`upgrade()` method must be examined.

For information on the important information on see [Revision structure](#revision-structure).

To align your database with a specific revision (migration ID `e75fa022c781` aligns with the current state of
our database):

```bash
alembic stamp e75fa022c781
```

### Viewing migration history

```bash
alembic history
```

### Show your current revision

```bash
alembic current
```

### Upgrading

Manually upgrade your database to match the latest models:

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

To downgrade to the original state (not recommended) use:

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

This will create a new Python file under `[versions/](versions/)`.

For example:

```bash
alembic revision -m "added desc field to job"
```

We should see a new Python file created with a commit/ID prepended to your message:

`cb3cf47d9259_added_desc_field_to_job.py`

#### Automatic* revision

Alembic can attempt to work out the changes required to migrate your database if you ask it to create a revision using
the `--autogenerate` flag when creating a revision. This is the recommended way to create revisions in Lumigator.

```bash
alembic revision --autogenerate -m {Explanatory commit-like message}
```

Please note that 'automatic' doesn't mean this can be completely automated, as manual steps are still required in
**verifying** the output in the generated `upgrade()` and `downgrade()` methods.

#### Revision structure

The main parts of the migration Python files Alembic creates are:

| Name            | Purpose                                                                      |
|-----------------|------------------------------------------------------------------------------|
| `revision`      | ID of this migration                                                         |
| `down_revision` | ID of the previous revision (`None` when this is the first migration)        |
| `upgrade()`     | Function which handles changes required when upgrading to this migration     |
| `downgrade()`   | Function which handles changes required when downgrading from this migration |
