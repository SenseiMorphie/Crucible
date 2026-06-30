from backend.agents.base import call_llm, truncate
from backend.agents.search_tool import run_searches


def founder_node(state: dict) -> dict:
    idea = state.get("idea", "")
    print("\n" + "="*50 + "\n🧑  FOUNDER AGENT\n" + "="*50, flush=True)

    web = run_searches([
        f"{idea[:60]} startup similar companies existing solutions",
        f"{idea[:60]} problem validation user demand evidence",
    ])

    prompt = f"""You are an experienced startup founder. Analyse this startup idea and return a JSON object.

STARTUP IDEA: {idea}

SEARCH RESULTS:
{web or "(none)"}

Return ONLY valid JSON with these exact keys:
{{
  "problem": "The specific painful problem being solved with evidence (2-3 sentences)",
  "target_market": "Primary customer: exact job title, company size, industry, why they have budget",
  "mvp": "Exactly 3 features for v1. What to build first and why. What is explicitly cut.",
  "unique_value_proposition": "One sentence with a specific metric. What this does that competitors don't.",
  "problem_evidence": "Real evidence the problem exists — cite company names or statistics from search",
  "similar_companies": ["Company A (raised $X) — how this differs", "Company B — how this differs", "Company C — how this differs"],
  "success_factors": ["Critical factor 1", "Critical factor 2", "Critical factor 3"],
  "founder_market_fit": "What domain expertise the founding team MUST have to succeed"
}}"""

    raw = call_llm(prompt, temperature=0.3)
    return {"founder": {
        "problem":                  raw.get("problem", f"Solving a core problem in: {idea[:100]}"),
        "target_market":            raw.get("target_market", "Target market to be defined"),
        "mvp":                      raw.get("mvp", "MVP to be defined"),
        "unique_value_proposition": raw.get("unique_value_proposition", "UVP to be defined"),
        "problem_evidence":         raw.get("problem_evidence", ""),
        "similar_companies":        raw.get("similar_companies", []),
        "success_factors":          raw.get("success_factors", []),
        "founder_market_fit":       raw.get("founder_market_fit", ""),
    }}
