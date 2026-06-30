from backend.agents.base import call_llm, truncate, top
from backend.agents.search_tool import run_searches


def failure_node(state: dict) -> dict:
    idea     = state.get("idea", "")
    founder  = state.get("founder", {})
    investor = state.get("investor", {})
    print("\n" + "="*50 + "\n💀  FAILURE AGENT\n" + "="*50, flush=True)

    web = run_searches([
        f"{idea[:60]} failed startup shutdown why post-mortem",
        f"{idea[:60]} startup mistakes pitfalls lessons",
    ])

    prompt = f"""You are a startup post-mortem analyst. You study failure. Return a JSON analysis of how this startup could die.

STARTUP IDEA: {idea}
MVP: {truncate(founder.get('mvp',''), 150)}
TOP RISKS: {top(investor.get('risks',[]), 3, 100)}

SEARCH RESULTS:
{web or "(none)"}

Return ONLY valid JSON with these exact keys:
{{
  "failure_modes": [
    "Mode 1 — full causal chain: e.g. 'Premature scaling: raises $2M, hires 20 people before PMF, burns $150K/mo, runway ends month 14, forced shutdown'",
    "Mode 2 — full causal chain (distribution failure)",
    "Mode 3 — full causal chain (competitor response)",
    "Mode 4 — full causal chain (technical/scaling)",
    "Mode 5 — full causal chain (team/cofounder)",
    "Mode 6 — full causal chain (fundraising timing)"
  ],
  "mitigation_strategies": [
    "Mitigation 1: specific actionable countermeasure",
    "Mitigation 2",
    "Mitigation 3",
    "Mitigation 4",
    "Mitigation 5",
    "Mitigation 6"
  ],
  "failed_companies": [
    "Real Company (founded YEAR, raised $X, died YEAR): died because [specific reason]. Lesson: [takeaway]",
    "Real Company 2: died because [reason]. Lesson: [takeaway]",
    "Real Company 3: died because [reason]. Lesson: [takeaway]"
  ],
  "critical_success_factors": [
    "CSF 1: specific metric that must be green at month 6 or pivot",
    "CSF 2: distribution bet that must pay off",
    "CSF 3: hiring decision that cannot be wrong",
    "CSF 4: moat that must be built before competitors notice"
  ],
  "biggest_single_risk": "The ONE sentence that, if said by an investor, kills the deal AND is right",
  "runway_analysis": "Burn math: $1.5M seed at $X/mo burn = Y months. Must hit $Z MRR by month N to raise Series A.",
  "pivot_options": [
    "Pivot 1: if core product fails, adjacent problem same team can solve",
    "Pivot 2: alternative monetisation of same user base"
  ]
}}"""

    raw = call_llm(prompt, temperature=0.3)
    return {"failure": {
        "failure_modes":            raw.get("failure_modes", []),
        "mitigation_strategies":    raw.get("mitigation_strategies", []),
        "failed_companies":         raw.get("failed_companies", []),
        "critical_success_factors": raw.get("critical_success_factors", []),
        "biggest_single_risk":      raw.get("biggest_single_risk", ""),
        "runway_analysis":          raw.get("runway_analysis", ""),
        "pivot_options":            raw.get("pivot_options", []),
    }}
