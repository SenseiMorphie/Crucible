"""
FastAPI entry point.
Run: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""
import backend.config as cfg   # must be first — sets LangSmith env vars

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router

app = FastAPI(
    title="Startup Simulator API",
    description="Multi-agent AI startup simulation with live web search",
    version="2.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(router)


@app.on_event("startup")
async def on_startup():
    print("\n" + "="*60)
    print("  🚀  Startup Simulator API v2.0")
    print(f"  LLM  : {cfg.LLM_PROVIDER} / {cfg.OPENROUTER_MODEL if cfg.LLM_PROVIDER=='openrouter' else cfg.OLLAMA_MODEL}")
    print(f"  Search: {'enabled ✅' if cfg.USE_WEB_SEARCH else 'disabled ❌'}")
    ls = cfg.LANGSMITH_TRACING.lower() == "true" and bool(cfg.LANGSMITH_API_KEY)
    print(f"  LangSmith: {'enabled ✅  → https://smith.langchain.com' if ls else 'disabled (set LANGSMITH_TRACING=true in .env)'}")
    print("  Docs : http://localhost:8000/docs")
    print("  Test LLM: http://localhost:8000/test-llm")
    print("="*60)

    # Quick LLM connectivity test
    print("\n  Testing LLM connection...", flush=True)
    try:
        from backend.agents.base import call_llm
        r = call_llm('Return JSON: {"status": "ok"}', temperature=0)
        if r.get("status") == "ok":
            print("  ✅  LLM connection OK\n")
        else:
            print(f"  ⚠️   LLM responded but unexpected: {r}\n")
    except Exception as e:
        print(f"  ❌  LLM FAILED: {e}")
        print("  → Open your .env file and check OPENROUTER_API_KEY\n")
