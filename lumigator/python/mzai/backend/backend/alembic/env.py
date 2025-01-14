import os
from logging.config import fileConfig

from alembic import context
from backend.records.base import BaseRecord
from backend.records.datasets import *  # noqa: F403
from backend.records.experiments import *  # noqa: F403
from backend.records.jobs import *  # noqa: F403
from sqlalchemy import engine_from_config, pool

"""
NOTE: Do NOT remove imports for the data models: backend.records.{package}
Some may appear to be unused, but they are required in order for the BaseRecord's
metadata to be populated correctly when it is used by Alembic as 'target_metadata'.

If a new data model package is added, then it MUST be manually imported here!
"""


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = BaseRecord.metadata

# Override the SQLAlchemy URL with the one we have stored in our environment.
config.set_main_option(
    "sqlalchemy.url",
    os.environ.get("SQLALCHEMY_DATABASE_URL", config.get_main_option("sqlalchemy.url")),
)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # SQLite does not support altering tables. To work around this, we need to enable the
        # generation of batch mode operations. This means that Alembic will create a new table with
        # the constraint, copy the existing data over, and remove the old table.
        # See more here: https://alembic.sqlalchemy.org/en/latest/batch.html
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
