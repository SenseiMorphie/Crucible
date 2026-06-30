from backend.agents.base import call_llm, truncate
from backend.agents.search_tool import run_searches


def market_node(state: dict) -> dict:
    idea    = state.get("idea", "")
    problem = state.get("founder", {}).get("problem", "")
    print("\n" + "="*50 + "\n📈  MARKET AGENT\n" + "="*50, flush=True)

    web = run_searches([
        f"{idea[:60]} market size TAM revenue statistics 2024 2025",
        f"{idea[:60]} industry CAGR growth forecast",
    ])

    prompt = f"""You are a senior market research analyst. Return a JSON object analysing this market.

STARTUP IDEA: {idea}
PROBLEM: {truncate(problem, 200)}

SEARCH RESULTS:
{web or "(none)"}

Return ONLY valid JSON with these exact keys:
{{
  "market_size": "TAM/SAM/SOM with specific $ figures and source. e.g. 'TAM $47B (global, 2024), SAM $4B (India), SOM $80M (year 3 target)'",
  "growth_rate": "CAGR with source. e.g. '22% CAGR 2024-2029 per MarketsandMarkets'",
  "market_statistics": ["Stat 1 with source", "Stat 2", "Stat 3", "Stat 4"],
  "opportunities": ["Opportunity 1 with data", "Opportunity 2", "Opportunity 3", "Opportunity 4"],
  "trends": ["Trend 1 with evidence", "Trend 2", "Trend 3"],
  "revenue_models": ["Model 1: exact pricing e.g. $49/seat/mo", "Model 2", "Model 3"],
  "target_segments": ["Segment 1: definition + size estimate", "Segment 2", "Segment 3"],
  "why_now": "Why 2025 is the right time — specific technology, regulation, or behaviour shift"
}}"""

    raw = call_llm(prompt, temperature=0.2)
    return {"market": {
        "market_size":       raw.get("market_size", "Market size analysis pending"),
        "growth_rate":       raw.get("growth_rate", ""),
        "opportunities":     raw.get("opportunities", []),
        "trends":            raw.get("trends", []),
        "market_statistics": raw.get("market_statistics", []),
        "revenue_models":    raw.get("revenue_models", []),
        "target_segments":   raw.get("target_segments", []),
        "why_now":           raw.get("why_now", ""),
    }}
