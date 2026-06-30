from backend.agents.base import call_llm, truncate
from backend.agents.search_tool import run_searches


def india_policy_node(state: dict) -> dict:
    idea   = state.get("idea", "")
    market = state.get("market", {})
    print("\n" + "="*50 + "\n🇮🇳  INDIA POLICY AGENT\n" + "="*50, flush=True)

    web = run_searches([
        f"India government scheme grant startup {idea[:50]} 2024",
        f"DPIIT startup india {idea[:45]} subsidy eligibility",
    ])

    prompt = f"""You are an Indian startup policy expert who has helped 150+ startups get DPIIT recognition and government grants.

STARTUP IDEA: {idea}
MARKET: {truncate(market.get('market_size',''), 100)}

SEARCH RESULTS:
{web or "(none — use your knowledge of Indian startup ecosystem)"}

Return ONLY valid JSON with these exact keys:
{{
  "startup_india_eligibility": "Yes/No + reasoning. Steps to apply at startupindia.gov.in for DPIIT recognition.",
  "dpiit_benefits": [
    "3-year income tax exemption under Section 80-IAC — save 25-30% of profits",
    "Angel Tax exemption under Section 56(2)(viib) — investors can invest above FMV tax-free",
    "Self-certification for 9 labour laws — no inspector visits for 3-5 years",
    "80% rebate on patent filing fees via IP facilitation cell",
    "Fast-track patent examination"
  ],
  "government_schemes": [
    "Startup India Seed Fund Scheme (SISFS): up to Rs 20L for proof-of-concept, Rs 50L for prototype. Apply via DPIIT-recognised incubators.",
    "Atal Innovation Mission (AIM): Atal Incubation Centres grant up to Rs 10Cr over 5 years. Atal New India Challenge Rs 50L-1.5Cr.",
    "NIDHI by DST: PRAYAS grants Rs 10L for prototype, EIR stipend Rs 30K/mo, SSS scheme.",
    "Sector-specific scheme most relevant to this idea with amount",
    "MSME/SIDBI scheme relevant to this idea"
  ],
  "grants_and_subsidies": [
    "DST-SERB SPARK: Rs 30L for early-stage tech validation",
    "BIRAC BIG Grant: Rs 50L if any biotech component",
    "SIDBI Fund of Funds: Rs 10000Cr corpus via SEBI-registered AIFs — access through Blume, Kalaari, Matrix",
    "State-specific grant relevant to this category with amount",
    "MUDRA Tarun loan up to Rs 10L for micro-enterprise component"
  ],
  "tax_benefits": [
    "Section 80-IAC: 100% tax deduction for 3 years out of 10 from incorporation. Apply to IMTAC.",
    "Angel Tax (56(2)(viib)) exemption: DPIIT-recognised startups fully exempt.",
    "ESOP tax deferral: employees pay tax at sale, not at exercise (Finance Act 2020).",
    "Section 35(2AB): 150% weighted deduction on R&D if DSIR-approved.",
    "GST benefit specific to this product category if applicable"
  ],
  "regulatory_requirements": [
    "Incorporate as Pvt Ltd on MCA21 (Rs 7-15K via CA). Get PAN, TAN, bank account.",
    "Apply for DPIIT recognition at startupindia.gov.in (free, 2 business days).",
    "Sector-specific regulator for this idea (e.g. RBI for fintech, SEBI for wealthtech, FSSAI for foodtech, IRDAI for insurtech)",
    "DPDP Act 2023 compliance if handling Indian user data — appoint DPO if processing sensitive data.",
    "FDI compliance if raising foreign funding — file FC-GPR with RBI within 30 days."
  ],
  "indian_vcs": [
    "Blume Ventures (Mumbai): Rs 50L-2Cr seed. Portfolio: Unacademy, Dunzo. Apply: blume.vc/apply",
    "Accel India (Bangalore): $500K-$3M Series A. Portfolio: Flipkart, Swiggy, Freshworks.",
    "Elevation Capital (Delhi): Seed to Series B $1-15M. Portfolio: Meesho, ShareChat.",
    "Matrix Partners India: Seed to Series B. Portfolio: Ola, Practo, Razorpay.",
    "3one4 Capital (Bangalore): Rs 50L-5Cr seed. Portfolio: Licious, Darwinbox.",
    "Stellaris VP: $250K-$3M seed. Portfolio: Mamaearth, mFine.",
    "100X.VC: Pre-seed Rs 25L-1Cr cohort model.",
    "Pi Ventures: Deep tech/AI focus, Rs 50L-2Cr."
  ],
  "accelerators_incubators": [
    "Y Combinator: $500K for 7%. India cohort 15-20 startups/batch. Apply: ycombinator.com",
    "Sequoia Surge: $1-2M for 10-15%. Southeast Asia + India cohort.",
    "T-Hub Hyderabad: Telangana govt-backed. Lab32 accelerator, free for selected startups.",
    "NASSCOM 10000 Startups: Free mentorship, $100K+ cloud credits.",
    "IIT/IIM incubators: SINE (IIT Bombay), NSRCEL (IIM Bangalore). Seed Rs 10-50L.",
    "Kerala Startup Mission (KSUM): Rs 10L grants for Kerala-based startups."
  ],
  "state_incentives": [
    "Karnataka (Startup Karnataka): Elevate 100 — top 100 startups get Rs 50L grant + mentorship.",
    "Telangana (T-Hub): iDISCO initiative, TS-iPASS single-window clearance.",
    "Maharashtra: MCED grants Rs 10-25L, 25% capital subsidy on plant/machinery.",
    "Gujarat (iCreate): SSIP grants up to Rs 2L per student startup, GVFL early-stage funding.",
    "Best state for this specific startup based on target market — explain why"
  ],
  "key_indian_markets": [
    "Tier 1 city 1 — reason with market size estimate",
    "Tier 1 city 2 — reason",
    "Tier 2 expansion target — when (after what milestone)",
    "Rural/semi-urban opportunity if applicable"
  ],
  "compliance_checklist": [
    "Week 1: Incorporate Pvt Ltd on MCA21 (Rs 7-15K). Get PAN, TAN, current account.",
    "Week 2: Apply for DPIIT recognition at startupindia.gov.in (free, 2 days).",
    "Month 1: Register for GST if turnover expected >Rs 20L/yr.",
    "Month 1: Apply for relevant sector licence if needed.",
    "Month 3: File for 80-IAC exemption with IMTAC after first full year of accounts.",
    "Before fundraising: Set up ESOP pool (10-15%), get valuation certificate from CA.",
    "Before foreign investment: Ensure FDI compliance, prepare FC-GPR filing."
  ]
}}"""

    raw = call_llm(prompt, temperature=0.3)
    return {"india_policy": {
        "startup_india_eligibility": raw.get("startup_india_eligibility", "Likely eligible — apply at startupindia.gov.in"),
        "dpiit_benefits":            raw.get("dpiit_benefits", []),
        "government_schemes":        raw.get("government_schemes", []),
        "grants_and_subsidies":      raw.get("grants_and_subsidies", []),
        "tax_benefits":              raw.get("tax_benefits", []),
        "regulatory_requirements":   raw.get("regulatory_requirements", []),
        "indian_vcs":                raw.get("indian_vcs", []),
        "accelerators_incubators":   raw.get("accelerators_incubators", []),
        "state_incentives":          raw.get("state_incentives", []),
        "key_indian_markets":        raw.get("key_indian_markets", []),
        "compliance_checklist":      raw.get("compliance_checklist", []),
    }}
