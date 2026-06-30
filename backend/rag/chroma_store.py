from __future__ import annotations
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings  # type: ignore

from backend.config import CHROMA_DB_DIR

_embedder = None

def _get_embedder():
    global _embedder
    if _embedder is None:
        print("   [Chroma] Loading embedding model...", flush=True)
        _embedder = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        print("   [Chroma] Ready ✅", flush=True)
    return _embedder

def _get_store():
    return Chroma(
        collection_name="startup_reports",
        embedding_function=_get_embedder(),
        persist_directory=CHROMA_DB_DIR,
    )

def _L(items): return " | ".join(str(i) for i in items) if items else ""

def _flatten(report: dict) -> str:
    f=report.get("founder",{}); m=report.get("market",{}); c=report.get("competitor",{})
    cu=report.get("customer",{}); inv=report.get("investor",{}); fl=report.get("failure",{})
    ip=report.get("india_policy",{}); j=report.get("judge",{})
    return "\n".join(filter(None,[
        f"STARTUP: {report.get('idea','')}",
        f"PROBLEM: {f.get('problem','')}",
        f"MVP: {f.get('mvp','')}",
        f"UVP: {f.get('unique_value_proposition','')}",
        f"TARGET MARKET: {f.get('target_market','')}",
        f"SIMILAR COMPANIES: {_L(f.get('similar_companies',[]))}",
        f"MARKET SIZE: {m.get('market_size','')}",
        f"GROWTH RATE: {m.get('growth_rate','')}",
        f"WHY NOW: {m.get('why_now','')}",
        f"MARKET STATS: {_L(m.get('market_statistics',[]))}",
        f"REVENUE MODELS: {_L(m.get('revenue_models',[]))}",
        f"COMPETITORS: {_L(c.get('competitors',[]))}",
        f"MARKET GAPS: {_L(c.get('gaps',[]))}",
        f"MOAT: {c.get('competitive_advantage','')}",
        f"POSITIONING: {c.get('positioning_strategy','')}",
        f"PERSONAS: {_L(cu.get('personas',[]))}",
        f"PAIN POINTS: {_L(cu.get('pain_points',[]))}",
        f"WTP: {cu.get('willingness_to_pay','')}",
        f"EARLY ADOPTER: {cu.get('early_adopter_profile','')}",
        f"CHANNELS: {_L(cu.get('acquisition_channels',[]))}",
        f"INVESTMENT SCORE: {inv.get('investment_score',0)}/10",
        f"RISKS: {_L(inv.get('risks',[]))}",
        f"STRENGTHS: {_L(inv.get('strengths',[]))}",
        f"RELEVANT INVESTORS: {_L(inv.get('relevant_investors',[]))}",
        f"FUNDING STAGE: {inv.get('funding_stage','')}",
        f"SUGGESTED RAISE: {inv.get('suggested_raise','')}",
        f"EXIT: {inv.get('exit_potential','')}",
        f"BIGGEST RISK: {fl.get('biggest_single_risk','')}",
        f"FAILURE MODES: {_L(fl.get('failure_modes',[]))}",
        f"FAILED COMPANIES: {_L(fl.get('failed_companies',[]))}",
        f"RUNWAY: {fl.get('runway_analysis','')}",
        # India policy
        f"STARTUP INDIA ELIGIBLE: {ip.get('startup_india_eligibility','')}",
        f"DPIIT BENEFITS: {_L(ip.get('dpiit_benefits',[]))}",
        f"GOVT SCHEMES: {_L(ip.get('government_schemes',[]))}",
        f"GRANTS SUBSIDIES: {_L(ip.get('grants_and_subsidies',[]))}",
        f"TAX BENEFITS: {_L(ip.get('tax_benefits',[]))}",
        f"INDIAN VCS: {_L(ip.get('indian_vcs',[]))}",
        f"ACCELERATORS: {_L(ip.get('accelerators_incubators',[]))}",
        f"STATE INCENTIVES: {_L(ip.get('state_incentives',[]))}",
        f"COMPLIANCE: {_L(ip.get('compliance_checklist',[]))}",
        # Judge
        f"FINAL SCORE: {j.get('final_score',0)}/100",
        f"VERDICT: {j.get('verdict','')}",
        f"ONE LINE: {j.get('one_line_verdict','')}",
        f"SUMMARY: {j.get('summary','')}",
        f"RECOMMENDATIONS: {_L(j.get('recommendations',[]))}",
        f"GO TO MARKET: {j.get('go_to_market','')}",
        f"90 DAY PLAN: {_L(j.get('action_plan_90_days',[]))}",
    ]))


def index_report(sim_id: str, report: dict) -> int:
    text   = _flatten(report)
    chunks = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=60).split_text(text)
    store  = _get_store()
    try:
        ex = store.get(where={"simulation_id": sim_id})
        if ex and ex.get("ids"): store.delete(ids=ex["ids"])
    except: pass
    store.add_texts(texts=chunks,
                    metadatas=[{"simulation_id": sim_id} for _ in chunks],
                    ids=[f"{sim_id}_c{i}" for i in range(len(chunks))])
    print(f"   [Chroma] Indexed {len(chunks)} chunks ✅", flush=True)
    return len(chunks)


def retrieve_chunks(sim_id: str, question: str, k: int = 5) -> list[str]:
    try:
        docs = _get_store().as_retriever(
            search_type="similarity",
            search_kwargs={"k": k, "filter": {"simulation_id": sim_id}},
        ).invoke(question)
        return [d.page_content for d in docs]
    except Exception as e:
        print(f"   [Chroma] Retrieval error: {e}", flush=True)
        return []
