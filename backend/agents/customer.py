from backend.agents.base import call_llm, truncate
from backend.agents.search_tool import run_searches


def customer_node(state: dict) -> dict:
    idea   = state.get("idea", "")
    target = state.get("founder", {}).get("target_market", "")
    print("\n" + "="*50 + "\n👥  CUSTOMER AGENT\n" + "="*50, flush=True)

    web = run_searches([
        f"{idea[:60]} user pain points complaints Reddit reviews",
        f"{idea[:60]} target customers demographics acquisition",
    ])

    prompt = f"""You are a UX researcher with 1000+ customer interviews. Return a JSON object about the target customers.

STARTUP IDEA: {idea}
TARGET: {truncate(target, 150)}

SEARCH RESULTS:
{web or "(none)"}

Return ONLY valid JSON with these exact keys:
{{
  "personas": [
    "Name, Age, Job Title at Company Type. Daily pain: [specific]. Uses [competitor] but hates [specific problem]. Would pay $X/mo.",
    "Name, Age, Job Title. Daily pain: [specific]. Would pay $X/mo.",
    "Name, Age, Job Title. Daily pain: [specific]. Budget situation."
  ],
  "pain_points": [
    "Pain in user's voice: 'I spend X hours/week doing Y manually because...'",
    "Pain in user's voice",
    "Pain in user's voice",
    "Pain in user's voice",
    "Pain in user's voice"
  ],
  "acquisition_channels": [
    "Channel 1: exact tactic + estimated CAC + why it works",
    "Channel 2: exact tactic + CAC",
    "Channel 3: exact tactic + CAC",
    "Channel 4: exact tactic + CAC"
  ],
  "community_insights": ["What users say online about this problem", "Common complaint pattern 1", "Common complaint pattern 2", "What they wish existed"],
  "willingness_to_pay": "Specific price range with reasoning. e.g. '$29-49/mo for SMB; $500+/mo enterprise. Users pay when they save X hrs/week.'",
  "customer_journey": "7 steps: Trigger event -> Search query they use -> How they discover product -> What they check first -> Trial friction -> Aha moment -> Converts to paid when [condition]",
  "early_adopter_profile": "First 100 customers: exact LinkedIn search query to find them, where they hang out online, why they'll bet on unproven product"
}}"""

    raw = call_llm(prompt, temperature=0.4)
    return {"customer": {
        "personas":              raw.get("personas", []),
        "pain_points":           raw.get("pain_points", []),
        "acquisition_channels":  raw.get("acquisition_channels", []),
        "community_insights":    raw.get("community_insights", []),
        "willingness_to_pay":    raw.get("willingness_to_pay", ""),
        "customer_journey":      raw.get("customer_journey", ""),
        "early_adopter_profile": raw.get("early_adopter_profile", ""),
    }}
