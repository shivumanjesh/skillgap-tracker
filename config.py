import os
import secrets


class Config:
    # Use environment variable in production; generate a secure key fallback if not provided
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

    # Standardize database URI (e.g. Render/Supabase postgres:// -> postgresql:// for SQLAlchemy)
    _db_url = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
