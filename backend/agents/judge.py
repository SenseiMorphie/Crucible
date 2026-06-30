"""
Judge Agent — final verdict.

KEY FIX: Uses truncate() and top() on every previous agent's output
so the total prompt stays under ~1500 tokens regardless of how verbose
the other agents were. This prevents the token-limit crash on free models.
"""
from backend.agents.base import call_llm, truncate, top


def judge_node(state: dict) -> dict:
    idea = state.get("idea", "")
    f    = state.get("founder",      {})
    m    = state.get("market",       {})
    c    = state.get("competitor",   {})
    cu   = state.get("customer",     {})
    inv  = state.get("investor",     {})
    fl   = state.get("failure",      {})
    ip   = state.get("india_policy", {})

    print("\n" + "="*50 + "\n⚖️   JUDGE AGENT\n" + "="*50, flush=True)

    # ── Build a SHORT summary (target: under 1200 tokens of input) ────────────
    summary = f"""IDEA: {idea}

FOUNDER:
  Problem: {truncate(f.get('problem',''), 200)}
  MVP: {truncate(f.get('mvp',''), 150)}
  UVP: {truncate(f.get('unique_value_proposition',''), 150)}

MARKET:
  Size: {truncate(m.get('market_size',''), 120)}
  CAGR: {truncate(m.get('growth_rate',''), 80)}
  Why Now: {truncate(m.get('why_now',''), 150)}

COMPETITION:
  Moat: {truncate(c.get('competitive_advantage',''), 150)}
  Positioning: {truncate(c.get('positioning_strategy',''), 150)}

CUSTOMER:
  WTP: {truncate(cu.get('willingness_to_pay',''), 100)}
  Early Adopter: {truncate(cu.get('early_adopter_profile',''), 120)}

INVESTOR:
  Score: {inv.get('investment_score',0)}/10
  Top Strength: {truncate(top(inv.get('strengths',[]), 1, 150), 150)}
  Top Risk: {truncate(top(inv.get('risks',[]), 1, 150), 150)}
  Raise: {truncate(inv.get('suggested_raise',''), 120)}

FAILURE:
  Biggest Risk: {truncate(fl.get('biggest_single_risk',''), 150)}
  Runway: {truncate(fl.get('runway_analysis',''), 120)}

INDIA:
  DPIIT: {truncate(ip.get('startup_india_eligibility',''), 100)}
  Key Scheme: {truncate(top(ip.get('government_schemes',[]), 1, 120), 120)}"""

    prompt = f"""You are a YC group partner giving a 3-minute verdict. Be direct, specific, and honest.

{summary}

Return ONLY a valid JSON object with EXACTLY these keys:

{{
  "final_score": <integer 0-100. Most ideas score 35-65. 70+ means genuinely strong.>,
  "verdict": "<Proceed OR Pivot OR Abandon>",
  "one_line_verdict": "One punchy sentence — the single most important thing a founder needs to hear",
  "summary": "3 sentences: (1) The real strength. (2) The single most likely way this dies. (3) Net conclusion.",
  "recommendations": [
    "Rec 1: actionable TODAY — specific enough to do tomorrow",
    "Rec 2: actionable THIS WEEK",
    "Rec 3: actionable THIS MONTH",
    "Rec 4: before raising — specific milestone",
    "Rec 5: the one thing to avoid at all costs"
  ],
  "go_to_market": "Specific GTM for first 90 days: which channel, which ICP (with LinkedIn search query), what to charge first 10 customers, what metric proves it is working.",
  "action_plan_90_days": [
    "Days 1-30: [3 specific tasks]. Success = [specific metric]. Stop and reassess if not hit.",
    "Days 31-60: [3 specific tasks]. Success = [specific metric].",
    "Days 61-90: [3 specific tasks]. Success = [specific metric]. If hit, ready to raise."
  ],
  "key_metrics": [
    "North Star: [metric] — target [number] by [date]",
    "Week 1: [measurable metric]",
    "Month 1: [threshold that proves demand]",
    "Month 3: [threshold that proves retention]"
  ],
  "scoring_breakdown": {{
    "problem_strength": <0-20>,
    "market_opportunity": <0-20>,
    "competitive_position": <0-20>,
    "team_execution": <0-20>,
    "financial_viability": <0-20>
  }}
}}

SCORING: 0-30=Abandon, 31-59=Pivot, 60-74=Proceed with caution, 75+=Strong proceed."""

    raw = call_llm(prompt, temperature=0.1)

    # ── Validate and set score/verdict ────────────────────────────────────────
    score = raw.get("final_score", 0)
    try:
        score = max(0, min(100, int(score)))
    except (TypeError, ValueError):
        score = 0

    verdict = raw.get("verdict", "")
    if verdict not in ("Proceed", "Pivot", "Abandon"):
        verdict = "Proceed" if score >= 60 else ("Abandon" if score <= 30 else "Pivot")

    # ── Fallback if LLM returned nothing ─────────────────────────────────────
    if not raw:
        print("      -> Judge LLM returned empty — building fallback verdict", flush=True)
        inv_score = inv.get("investment_score", 5)
        score     = min(100, max(0, inv_score * 7 + len(f.get('similar_companies',[])) * 3))
        verdict   = "Proceed" if score >= 60 else ("Abandon" if score <= 30 else "Pivot")
        raw = {
            "one_line_verdict":   f"Simulation complete — review each agent's analysis for detailed insights.",
            "summary":            f"The idea addresses {truncate(f.get('problem','a real problem'), 100)}. "
                                  f"Market is {truncate(m.get('market_size','potentially large'), 80)}. "
                                  f"Investor score was {inv_score}/10.",
            "recommendations":    [
                "Validate the problem with 20+ customer interviews before building",
                "Define your unfair advantage vs existing competitors",
                "Set a revenue target before raising",
                "Apply for DPIIT recognition immediately (free, takes 2 days)",
                "Build in public — early distribution beats late product",
            ],
            "go_to_market":       "Start with direct outreach to early adopters. Charge from day 1.",
            "action_plan_90_days": [
                "Days 1-30: 30 customer interviews, validate WTP, build landing page",
                "Days 31-60: Launch MVP to 10 beta users, track D7/D30 retention",
                "Days 61-90: Reach $5K MRR or 50 active users, begin investor conversations",
            ],
            "key_metrics":        [
                "North Star: Weekly Active Users or MRR",
                "Week 1: 5 customer interviews completed",
                "Month 1: 3 paying customers",
                "Month 3: D30 retention >25%",
            ],
            "scoring_breakdown": {
                "problem_strength":    min(20, int(inv_score * 2)),
                "market_opportunity":  min(20, int(inv_score * 2)),
                "competitive_position":min(20, 10),
                "team_execution":      min(20, 10),
                "financial_viability": min(20, int(inv_score * 1.5)),
            },
        }

    print(f"\n{'='*50}\n✅  SIMULATION COMPLETE\n    Score: {score}/100  |  Verdict: {verdict}\n{'='*50}\n", flush=True)

    return {"judge": {
        "final_score":         score,
        "verdict":             verdict,
        "one_line_verdict":    raw.get("one_line_verdict", ""),
        "summary":             raw.get("summary", ""),
        "recommendations":     raw.get("recommendations", []),
        "go_to_market":        raw.get("go_to_market", ""),
        "action_plan_90_days": raw.get("action_plan_90_days", []),
        "key_metrics":         raw.get("key_metrics", []),
        "scoring_breakdown":   raw.get("scoring_breakdown", {}),
    }}
