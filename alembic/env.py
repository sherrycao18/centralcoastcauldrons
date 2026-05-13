from logging.config import fileConfig
import os

from sqlalchemy import create_engine, pool
from alembic import context

# Alembic Config object
config = context.config


def normalize_postgres_uri(uri: str) -> str:
    """Match driver to psycopg v3 (avoid SQLAlchemy defaulting to psycopg2)."""
    cleaned = uri.strip()
    if cleaned.startswith("postgresql+psycopg://"):
        out = cleaned
    elif cleaned.startswith("postgresql+psycopg2://"):
        out = "postgresql+psycopg://" + cleaned.removeprefix("postgresql+psycopg2://")
    elif cleaned.startswith("postgres://"):
        out = "postgresql+psycopg://" + cleaned.removeprefix("postgres://")
    elif cleaned.startswith("postgresql://"):
        out = "postgresql+psycopg://" + cleaned.removeprefix("postgresql://")
    else:
        out = cleaned
    # Supabase expects TLS; pooler URLs often omit sslmode.
    if "supabase" in out and "sslmode=" not in out:
        sep = "&" if "?" in out else "?"
        out = f"{out}{sep}sslmode=require"
    return out


def get_database_url() -> str:
    """POSTGRES_URI must not go through ConfigParser: URLs often contain %xx escapes."""
    raw = os.getenv(
        "POSTGRES_URI",
        "postgresql+psycopg://myuser:mypassword@localhost/mydatabase",
    )
    return normalize_postgres_uri(raw)

# Set up logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your metadata (for `--autogenerate`)
# from app.db import Base
target_metadata = None  # or Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_database_url()
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
    connectable = create_engine(get_database_url(), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# Entry point
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
