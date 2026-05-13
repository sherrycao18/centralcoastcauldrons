from dotenv import load_dotenv, find_dotenv
import os
from functools import lru_cache

# Load default first
load_dotenv(dotenv_path="default.env", override=False)

# Then override with .env if available
load_dotenv(dotenv_path=find_dotenv(".env"), override=True)

def normalize_postgres_uri(uri: str) -> str:
    """
    Normalize common Postgres URL schemes to the driver we ship (psycopg v3).

    Render/Supabase UIs often provide `postgres://` or `postgresql://` URLs.
    SQLAlchemy treats those as the legacy default driver (psycopg2) unless the
    driver is specified explicitly.
    """
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
    if "supabase" in out and "sslmode=" not in out:
        sep = "&" if "?" in out else "?"
        out = f"{out}{sep}sslmode=require"
    return out


class Settings:
    API_KEY: str | None = os.getenv("API_KEY")
    POSTGRES_URI: str | None = os.getenv("POSTGRES_URI")

    def __init__(self):
        if not self.API_KEY:
            raise ValueError("API_KEY is missing in the environment variables.")
        if not self.POSTGRES_URI:
            raise ValueError("POSTGRES_URI is missing in the environment variables.")
        self.POSTGRES_URI = normalize_postgres_uri(self.POSTGRES_URI)


@lru_cache()
def get_settings():
    return Settings()
