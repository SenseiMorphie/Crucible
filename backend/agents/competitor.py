from backend.agents.base import call_llm, truncate
from backend.agents.search_tool import run_searches


def competitor_node(state: dict) -> dict:
    idea = state.get("idea", "")
    print("\n" + "="*50 + "\n🎯  COMPETITOR AGENT\n" + "="*50, flush=True)

    web = run_searches([
        f"{idea[:60]} competitors alternatives companies",
        f"{idea[:60]} market leader startup funding 2024",
    ])

    prompt = f"""You are a competitive intelligence analyst. Return a JSON object mapping the competitive landscape.

STARTUP IDEA: {idea}

SEARCH RESULTS:
{web or "(none — use your training knowledge)"}

Return ONLY valid JSON with these exact keys:
{{
  "competitors": [
    "Company Name (founded YEAR, raised $X) — what they do and key weakness",
    "Company Name (founded YEAR, raised $X) — what they do and key weakness",
    "Company Name (founded YEAR, raised $X) — what they do and key weakness",
    "Company Name — description",
    "Company Name — description"
  ],
  "competitor_details": [
    {{"name": "Company 1", "funding": "$X Series Y", "strengths": ["s1", "s2"], "weaknesses": ["w1", "w2"], "how_to_beat": "specific tactic"}},
    {{"name": "Company 2", "funding": "$X", "strengths": ["s1"], "weaknesses": ["w1", "w2"], "how_to_beat": "specific tactic"}},
    {{"name": "Company 3", "funding": "$X", "strengths": ["s1"], "weaknesses": ["w1"], "how_to_beat": "specific tactic"}}
  ],
  "gaps": ["Gap 1: underserved need all competitors miss", "Gap 2", "Gap 3", "Gap 4"],
  "competitive_advantage": "The ONE defensible moat: network effects / data / switching costs / distribution",
  "market_map": "2 sentences: who are incumbents, who are challengers, where is white space",
  "positioning_strategy": "Fill in: We are [X] for [customer] frustrated by [competitor] because [reason]. We win by [differentiator]."
}}"""

    raw = call_llm(prompt, temperature=0.2)
    return {"competitor": {
        "competitors":           raw.get("competitors", []),
        "competitor_details":    raw.get("competitor_details", []),
        "gaps":                  raw.get("gaps", []),
        "competitive_advantage": raw.get("competitive_advantage", ""),
        "market_map":            raw.get("market_map", ""),
        "positioning_strategy":  raw.get("positioning_strategy", ""),
    }}
