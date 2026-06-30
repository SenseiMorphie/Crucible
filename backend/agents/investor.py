from backend.agents.base import call_llm, truncate, top
from backend.agents.search_tool import run_searches


def investor_node(state: dict) -> dict:
    idea     = state.get("idea", "")
    founder  = state.get("founder", {})
    market   = state.get("market", {})
    customer = state.get("customer", {})
    print("\n" + "="*50 + "\n💼  INVESTOR AGENT\n" + "="*50, flush=True)

    web = run_searches([
        f"{idea[:55]} startup funding investors VC 2024",
        f"venture capital {idea[:55]} portfolio companies invested",
    ])

    prompt = f"""You are a VC partner evaluating an early-stage startup. Return a JSON investment assessment.

STARTUP IDEA: {idea}
PROBLEM: {truncate(founder.get('problem',''), 180)}
MARKET: {truncate(market.get('market_size',''), 120)}
WTP: {truncate(customer.get('willingness_to_pay',''), 100)}

SEARCH RESULTS:
{web or "(none)"}

Return ONLY valid JSON with these exact keys:
{{
  "investment_score": <integer 1-10>,
  "risks": ["Risk 1: specific concern with magnitude", "Risk 2", "Risk 3", "Risk 4", "Risk 5"],
  "strengths": ["Strength 1: why a VC would write a check", "Strength 2", "Strength 3", "Strength 4"],
  "concerns": "2-3 sentence honest debrief. What is the 'but' that might kill the deal?",
  "relevant_investors": [
    "VC Firm Name — why they invest here, real portfolio companies in this space",
    "VC Firm Name — why they invest here",
    "VC Firm Name — why they invest here",
    "VC Firm Name — why they invest here",
    "VC Firm Name — why they invest here",
    "Angel/micro-VC active in this space"
  ],
  "funding_examples": [
    "Company A raised $XM at what stage — traction at time of raise",
    "Company B raised $XM — what made investors write the check",
    "Company C raised $XM — comparable metrics"
  ],
  "funding_stage": "Pre-seed / Seed / Series A with reasoning",
  "suggested_raise": "Amount, valuation, use of funds, runway goal. e.g. '$1.5M pre-seed at $6M post, 18 months to $30K MRR'",
  "key_metrics_for_investors": ["Metric 1 threshold", "Metric 2 threshold", "Metric 3 threshold"],
  "exit_potential": "Strategic acquirers (name 3), IPO path, comparable exits with multiples"
}}"""

    raw = call_llm(prompt, temperature=0.2)
    score = raw.get("investment_score", 5)
    try: score = max(1, min(10, int(score)))
    except: score = 5
    return {"investor": {
        "investment_score":          score,
        "risks":                     raw.get("risks", []),
        "strengths":                 raw.get("strengths", []),
        "concerns":                  raw.get("concerns", ""),
        "relevant_investors":        raw.get("relevant_investors", []),
        "funding_examples":          raw.get("funding_examples", []),
        "funding_stage":             raw.get("funding_stage", ""),
        "suggested_raise":           raw.get("suggested_raise", ""),
        "key_metrics_for_investors": raw.get("key_metrics_for_investors", []),
        "exit_potential":            raw.get("exit_potential", ""),
    }}
