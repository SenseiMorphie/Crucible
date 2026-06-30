from __future__ import annotations
import uuid, traceback
from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from backend.models.schemas import (
    SimulationRequest, SimulationResponse, SimulationReport,
    SimulationSummary, HistoryResponse, AskRequest, AskResponse,
    FounderOutput, MarketOutput, CompetitorOutput, CustomerOutput,
    InvestorOutput, FailureOutput, IndiaPolicyOutput, JudgeOutput,
)
from backend.graph.workflow   import run_simulation
from backend.utils.storage    import (save_simulation, load_simulation,
                                      list_simulations, delete_simulation,
                                      save_chat, load_chat, delete_chat)
from backend.rag.chroma_store import index_report
from backend.rag.faiss_store  import save_faiss_index
from backend.rag.qa_chain     import answer_question

router = APIRouter()


# ── Health ────────────────────────────────────────────────────────────────────
@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/test-llm")
async def test_llm():
    try:
        from backend.agents.base import call_llm
        r = call_llm('Return JSON: {"status": "ok"}', temperature=0)
        return {"llm_ok": True, "response": r}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Simulate ──────────────────────────────────────────────────────────────────
@router.post("/simulate", response_model=SimulationResponse)
async def simulate(req: SimulationRequest):
    sim_id = str(uuid.uuid4())[:8]
    try:
        state = run_simulation(req.idea)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Simulation error: {e}")

    try:
        save_simulation(sim_id, req.idea, state)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Save error: {e}")

    # RAG indexing — non-critical, never fails the simulation
    report = load_simulation(sim_id)
    if report:
        try:
            index_report(sim_id, report)
        except Exception as e:
            print(f"[RAG] Chroma indexing skipped: {e}")
        try:
            save_faiss_index(sim_id, report)
        except Exception as e:
            print(f"[RAG] FAISS indexing skipped: {e}")

    return SimulationResponse(status="success", simulation_id=sim_id)


# ── History ───────────────────────────────────────────────────────────────────
@router.get("/history", response_model=HistoryResponse)
async def history():
    sims = list_simulations()
    return HistoryResponse(simulations=[SimulationSummary(**s) for s in sims], total=len(sims))


# ── Report ────────────────────────────────────────────────────────────────────
@router.get("/report/{sim_id}", response_model=SimulationReport)
async def report(sim_id: str):
    data = load_simulation(sim_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Simulation '{sim_id}' not found.")
    try:
        return SimulationReport(
            id=data["id"], idea=data["idea"],
            timestamp=data["timestamp"], status=data.get("status","completed"),
            founder=FounderOutput(**data.get("founder",{})),
            market=MarketOutput(**data.get("market",{})),
            competitor=CompetitorOutput(**data.get("competitor",{})),
            customer=CustomerOutput(**data.get("customer",{})),
            investor=InvestorOutput(**data.get("investor",{})),
            failure=FailureOutput(**data.get("failure",{})),
            india_policy=IndiaPolicyOutput(**data.get("india_policy",{})),
            judge=JudgeOutput(**data.get("judge",{})),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report parse error: {e}")

@router.delete("/report/{sim_id}")
async def delete_report(sim_id: str):
    delete_simulation(sim_id)
    return {"status": "deleted", "id": sim_id}


# ── PDF (lazy import so missing fpdf2 never breaks other routes) ──────────────
@router.get("/report/{sim_id}/pdf")
async def report_pdf(sim_id: str):
    data = load_simulation(sim_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Simulation '{sim_id}' not found.")
    try:
        from backend.utils.pdf_generator import generate_pdf
        pdf_bytes = generate_pdf(data)
    except ImportError:
        raise HTTPException(status_code=501,
            detail="fpdf2 not installed. Run: pip install fpdf2>=2.7.9")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF error: {e}")
    safe = "".join(c if c.isalnum() or c in "-_ " else "" for c in data.get("idea","report"))[:40]
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="startup_report_{safe.replace(" ","_")}.pdf"'},
    )
@router.get("/report/{sim_id}/debug")
async def debug_report(sim_id: str):
    data = load_simulation(sim_id)
    if not data:
        return {"error": "not found"}
    return {
        "top_level_keys": list(data.keys()),
        "has_founder":    "founder" in data,
        "has_market":     "market" in data,
        "has_judge":      "judge" in data,
        "founder_keys":   list(data.get("founder", {}).keys()) if isinstance(data.get("founder"), dict) else str(type(data.get("founder"))),
        "judge_keys":     list(data.get("judge", {}).keys()) if isinstance(data.get("judge"), dict) else str(type(data.get("judge"))),
    }

# ── Ask ───────────────────────────────────────────────────────────────────────
@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    if not load_simulation(req.simulation_id):
        raise HTTPException(status_code=404, detail=f"Simulation '{req.simulation_id}' not found.")
    try:
        answer, n = answer_question(req.simulation_id, req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return AskResponse(answer=answer, sources_used=n)


# ── Chat persistence ──────────────────────────────────────────────────────────
class ChatSaveRequest(BaseModel):
    messages: List[dict]

@router.get("/chat/{sim_id}")
async def get_chat(sim_id: str):
    return {"messages": load_chat(sim_id)}

@router.post("/chat/{sim_id}")
async def post_chat(sim_id: str, req: ChatSaveRequest):
    save_chat(sim_id, req.messages)
    return {"status": "saved"}

@router.delete("/chat/{sim_id}")
async def clear_chat_route(sim_id: str):
    delete_chat(sim_id)
    return {"status": "cleared"}

