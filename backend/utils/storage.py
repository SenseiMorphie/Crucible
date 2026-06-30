from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from backend.config import SIMULATIONS_DIR

_ROOT   = Path(SIMULATIONS_DIR)
_CHATS  = _ROOT / "chats"
_CHATS.mkdir(parents=True, exist_ok=True)


# ── helpers ───────────────────────────────────────────────────────────────────
def _idx():       return _ROOT / "_index.json"
def _rpt(sid):    return _ROOT / f"{sid}.json"
def _chat(sid):   return _CHATS / f"{sid}.json"

def _load_idx():
    p = _idx()
    if p.exists():
        try: return json.loads(p.read_text(encoding="utf-8"))
        except: return []
    return []

def _save_idx(idx):
    _idx().write_text(json.dumps(idx, indent=2, default=str), encoding="utf-8")


# ── simulation ────────────────────────────────────────────────────────────────
def save_simulation(sim_id: str, idea: str, state: dict) -> None:
    ts    = datetime.now(timezone.utc).isoformat()
    judge = state.get("judge", {})
    report = {
        "id": sim_id, "idea": idea, "timestamp": ts, "status": "completed",
        "founder":      state.get("founder",      {}),
        "market":       state.get("market",        {}),
        "competitor":   state.get("competitor",    {}),
        "customer":     state.get("customer",      {}),
        "investor":     state.get("investor",      {}),
        "failure":      state.get("failure",       {}),
        "india_policy": state.get("india_policy",  {}),
        "judge":        judge,
    }
    _rpt(sim_id).write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    idx = [e for e in _load_idx() if e.get("id") != sim_id]
    idx.insert(0, {"id": sim_id, "idea": idea, "timestamp": ts,
                   "final_score": judge.get("final_score", 0),
                   "verdict":     judge.get("verdict", "Unknown")})
    _save_idx(idx)


def load_simulation(sim_id: str) -> Optional[dict]:
    p = _rpt(sim_id)
    if not p.exists(): return None
    try: return json.loads(p.read_text(encoding="utf-8"))
    except: return None


def list_simulations() -> list:
    return _load_idx()


def delete_simulation(sim_id: str) -> None:
    p = _rpt(sim_id)
    if p.exists(): p.unlink()
    _save_idx([e for e in _load_idx() if e.get("id") != sim_id])
    delete_chat(sim_id)


# ── chat persistence ──────────────────────────────────────────────────────────
def save_chat(sim_id: str, messages: list) -> None:
    _chat(sim_id).write_text(json.dumps(messages, indent=2, ensure_ascii=False), encoding="utf-8")


def load_chat(sim_id: str) -> list:
    p = _chat(sim_id)
    if not p.exists(): return []
    try: return json.loads(p.read_text(encoding="utf-8"))
    except: return []


def delete_chat(sim_id: str) -> None:
    p = _chat(sim_id)
    if p.exists(): p.unlink()
