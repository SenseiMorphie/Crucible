import os
from pathlib import Path
from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env", override=True)

# ── LLM ──────────────────────────────────────────────────────────────────────
LLM_PROVIDER        = os.getenv("LLM_PROVIDER", "openrouter")
OPENROUTER_API_KEY  = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL    = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OLLAMA_MODEL        = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_BASE_URL     = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ── Features ──────────────────────────────────────────────────────────────────
USE_WEB_SEARCH = os.getenv("USE_WEB_SEARCH", "true").lower() == "true"

# ── Storage ───────────────────────────────────────────────────────────────────
DATA_DIR        = _ROOT / "data"
SIMULATIONS_DIR = DATA_DIR / "simulations"
CHROMA_DB_DIR   = str(DATA_DIR / "chroma_db")
FAISS_DIR       = DATA_DIR / "faiss"

for d in [SIMULATIONS_DIR, DATA_DIR / "chroma_db", FAISS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── LangSmith ─────────────────────────────────────────────────────────────────
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "startup-simulator")

if LANGSMITH_TRACING.lower() == "true" and LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"]     = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"]     = LANGSMITH_PROJECT
    os.environ["LANGSMITH_API_KEY"]     = LANGSMITH_API_KEY
