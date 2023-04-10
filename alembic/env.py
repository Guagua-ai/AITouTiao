from models.view_history import ViewHistory
from models.collection_tweet import CollectionsTweets
from models.collection import Collection
from models.user import User
from models.tweet import Tweet
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# create a new database engine
engine = create_engine(config.get_main_option('sqlalchemy.url'))

# bind the engine to the declarative base
Base = declarative_base()
Base.metadata.bind = engine

# create a new session factory
Session = sessionmaker(bind=engine)

# add your model's MetaData object here
# for 'autogenerate' support

target_metadata = Base.metadata


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
        # bind the connection to the declarative base
        Base.metadata.bind = connection
        # create the tables if they don't exist
        Base.metadata.create_all(connection)

        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
