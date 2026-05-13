from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config, pool
from alembic import context

# Prefer using the same POSTGRES_URI normalization as the app.
try:
    from src.config import normalize_postgres_uri
except Exception:  # pragma: no cover
    def normalize_postgres_uri(uri: str) -> str:
        cleaned = uri.strip()
        if cleaned.startswith("postgresql+psycopg://"):
            return cleaned
        if cleaned.startswith("postgresql+psycopg2://"):
            return "postgresql+psycopg://" + cleaned.removeprefix("postgresql+psycopg2://")
        if cleaned.startswith("postgres://"):
            return "postgresql+psycopg://" + cleaned.removeprefix("postgres://")
        if cleaned.startswith("postgresql://"):
            return "postgresql+psycopg://" + cleaned.removeprefix("postgresql://")
        return cleaned

# Alembic Config object
config = context.config

# Load DB URI from environment and override config
config.set_main_option(
    "sqlalchemy.url",
    normalize_postgres_uri(
        os.getenv(
            "POSTGRES_URI",
            "postgresql+psycopg://myuser:mypassword@localhost/mydatabase",
        )
    ),
)

# Set up logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your metadata (for `--autogenerate`)
# from app.db import Base
target_metadata = None  # or Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    if not configuration:
        raise Exception("No config section for Alembic")
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# Entry point
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
