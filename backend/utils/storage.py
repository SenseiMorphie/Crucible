"""
backend/utils/storage.py  —  MongoDB backend
"""
from __future__ import annotations
import os
from datetime import datetime, timezone
from typing import Optional

from pymongo import MongoClient, DESCENDING
from pymongo.collection import Collection
from pymongo.errors import PyMongoError


# ── connection ────────────────────────────────────────────────────────────────
_URI = os.environ.get("MONGO_URI", "")
_DB  = os.environ.get("MONGO_DB",  "startup_simulator")

if not _URI:
    raise EnvironmentError(
        "MONGO_URI is not set. Add it to your .env file."
    )

_client: MongoClient = MongoClient(_URI)
_db = _client[_DB]

_sims:  Collection = _db["simulations"]
_idx:   Collection = _db["sim_index"]
_chats: Collection = _db["chats"]

_sims.create_index("id",  unique=True)
_idx.create_index("id",   unique=True)
_idx.create_index([("timestamp", DESCENDING)])
_chats.create_index("sim_id", unique=True)


# ── internal helper ───────────────────────────────────────────────────────────
def _strip(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc.pop("_id")
    return doc


# ── simulation ────────────────────────────────────────────────────────────────
def save_simulation(sim_id: str, idea: str, state: dict) -> None:
    ts    = datetime.now(timezone.utc).isoformat()
    judge = state.get("judge", {})
    report = {
        "id": sim_id, "idea": idea, "timestamp": ts, "status": "completed",
        "founder":      state.get("founder",      {}),
        "market":       state.get("market",       {}),
        "competitor":   state.get("competitor",   {}),
        "customer":     state.get("customer",     {}),
        "investor":     state.get("investor",     {}),
        "failure":      state.get("failure",      {}),
        "india_policy": state.get("india_policy", {}),
        "judge":        judge,
    }
    _sims.replace_one({"id": sim_id}, report, upsert=True)
    _idx.replace_one({"id": sim_id}, {
        "id": sim_id, "idea": idea, "timestamp": ts,
        "final_score": judge.get("final_score", 0),
        "verdict":     judge.get("verdict", "Unknown"),
    }, upsert=True)


def load_simulation(sim_id: str) -> Optional[dict]:
    try:
        doc = _sims.find_one({"id": sim_id})
        return _strip(doc) if doc else None
    except PyMongoError as e:
        print(f"[MongoDB] load_simulation error: {e}")
        return None


def list_simulations() -> list:
    try:
        return list(_idx.find({}, {"_id": 0}).sort("timestamp", DESCENDING))
    except PyMongoError as e:
        print(f"[MongoDB] list_simulations error: {e}")
        return []


def delete_simulation(sim_id: str) -> None:
    try:
        _sims.delete_one({"id": sim_id})
        _idx.delete_one({"id": sim_id})
        delete_chat(sim_id)
    except PyMongoError as e:
        print(f"[MongoDB] delete_simulation error: {e}")


# ── chat ──────────────────────────────────────────────────────────────────────
def save_chat(sim_id: str, messages: list) -> None:
    try:
        _chats.replace_one(
            {"sim_id": sim_id},
            {"sim_id": sim_id, "messages": messages},
            upsert=True,
        )
    except PyMongoError as e:
        print(f"[MongoDB] save_chat error: {e}")


def load_chat(sim_id: str) -> list:
    try:
        doc = _chats.find_one({"sim_id": sim_id})
        return doc["messages"] if doc else []
    except PyMongoError as e:
        print(f"[MongoDB] load_chat error: {e}")
        return []


def delete_chat(sim_id: str) -> None:
    try:
        _chats.delete_one({"sim_id": sim_id})
    except PyMongoError as e:
        print(f"[MongoDB] delete_chat error: {e}")