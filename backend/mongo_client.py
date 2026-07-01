"""
MongoDB connection singleton.

Connects once, lazily, on first use. If the connection fails for any
reason (bad URI, network issue, IP not whitelisted on Atlas), it logs
the error and storage.py falls back to local JSON files automatically.
"""
from __future__ import annotations
import sys
import backend.config as cfg

_client = None
_db = None


def get_db():
    """Return the MongoDB database handle, or None if unavailable."""
    global _client, _db

    if not cfg.USE_MONGODB:
        return None

    if _db is not None:
        return _db

    try:
        from pymongo import MongoClient
        from pymongo.server_api import ServerApi

        _client = MongoClient(cfg.MONGO_URI, server_api=ServerApi("1"), serverSelectionTimeoutMS=5000)
        # Force a round-trip to confirm the connection actually works
        _client.admin.command("ping")
        _db = _client[cfg.MONGO_DB_NAME]
        print(f"   [Mongo] Connected to database '{cfg.MONGO_DB_NAME}' ✅", flush=True)
        return _db
    except Exception as e:
        print(f"   [Mongo] Connection failed — falling back to local JSON storage: {e}", file=sys.stderr)
        _db = None
        return None


def is_connected() -> bool:
    return get_db() is not None