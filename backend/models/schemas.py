from __future__ import annotations
from typing import List, Literal, Dict, Any
from pydantic import BaseModel, Field, field_validator


# ── generic coercion ──────────────────────────────────────────────────────────
def _to_list(v: Any) -> list:
    """Accept list, string, or None — always return a list."""
    if v is None:            return []
    if isinstance(v, list):  return v
    if isinstance(v, str):   return [v] if v.strip() else []
    return [str(v)]

def _to_int(v: Any, default: int = 0) -> int:
    try:    return max(0, int(v))
    except: return default


# ── Request models ────────────────────────────────────────────────────────────
class SimulationRequest(BaseModel):
    idea: str = Field(..., min_length=10)

class AskRequest(BaseModel):
    simulation_id: str
    question: str = Field(..., min_length=3)


# ── Agent output models ────────────────────────────────────────────────────────
class FounderOutput(BaseModel):
    problem:                  str       = ""
    target_market:            str       = ""
    mvp:                      str       = ""
    unique_value_proposition: str       = ""
    problem_evidence:         str       = ""
    similar_companies:        List[str] = []
    success_factors:          List[str] = []
    founder_market_fit:       str       = ""

    @field_validator("similar_companies","success_factors", mode="before")
    @classmethod
    def coerce(cls, v): return _to_list(v)


class MarketOutput(BaseModel):
    market_size:       str       = ""
    growth_rate:       str       = ""
    opportunities:     List[str] = []
    trends:            List[str] = []
    market_statistics: List[str] = []
    revenue_models:    List[str] = []
    target_segments:   List[str] = []
    why_now:           str       = ""

    @field_validator("opportunities","trends","market_statistics",
                     "revenue_models","target_segments", mode="before")
    @classmethod
    def coerce(cls, v): return _to_list(v)


class CompetitorOutput(BaseModel):
    competitors:           List[str]            = []
    competitor_details:    List[Dict[str, Any]] = []
    gaps:                  List[str]            = []
    competitive_advantage: str                  = ""
    market_map:            str                  = ""
    positioning_strategy:  str                  = ""

    @field_validator("competitors","gaps", mode="before")
    @classmethod
    def coerce(cls, v): return _to_list(v)

    @field_validator("competitor_details", mode="before")
    @classmethod
    def coerce_details(cls, v):
        if v is None:           return []
        if isinstance(v, list): return v
        return []


class CustomerOutput(BaseModel):
    personas:              List[str] = []
    pain_points:           List[str] = []
    acquisition_channels:  List[str] = []
    community_insights:    List[str] = []
    willingness_to_pay:    str       = ""
    customer_journey:      str       = ""
    early_adopter_profile: str       = ""

    @field_validator("personas","pain_points","acquisition_channels",
                     "community_insights", mode="before")
    @classmethod
    def coerce(cls, v): return _to_list(v)


class InvestorOutput(BaseModel):
    investment_score:          int       = 0
    risks:                     List[str] = []
    strengths:                 List[str] = []
    concerns:                  str       = ""
    relevant_investors:        List[str] = []
    funding_examples:          List[str] = []
    funding_stage:             str       = ""
    suggested_raise:           str       = ""
    key_metrics_for_investors: List[str] = []
    exit_potential:            str       = ""

    @field_validator("investment_score", mode="before")
    @classmethod
    def coerce_score(cls, v): return max(1, min(10, _to_int(v, 5)))

    @field_validator("risks","strengths","relevant_investors","funding_examples",
                     "key_metrics_for_investors", mode="before")
    @classmethod
    def coerce(cls, v): return _to_list(v)


class FailureOutput(BaseModel):
    failure_modes:            List[str] = []
    mitigation_strategies:    List[str] = []
    failed_companies:         List[str] = []
    critical_success_factors: List[str] = []
    biggest_single_risk:      str       = ""
    runway_analysis:          str       = ""
    pivot_options:            List[str] = []

    @field_validator("failure_modes","mitigation_strategies","failed_companies",
                     "critical_success_factors","pivot_options", mode="before")
    @classmethod
    def coerce(cls, v): return _to_list(v)


class IndiaPolicyOutput(BaseModel):
    startup_india_eligibility: str       = ""
    dpiit_benefits:            List[str] = []
    government_schemes:        List[str] = []
    grants_and_subsidies:      List[str] = []
    tax_benefits:              List[str] = []
    regulatory_requirements:   List[str] = []
    indian_vcs:                List[str] = []
    accelerators_incubators:   List[str] = []
    state_incentives:          List[str] = []
    key_indian_markets:        List[str] = []
    compliance_checklist:      List[str] = []

    @field_validator("dpiit_benefits","government_schemes","grants_and_subsidies",
                     "tax_benefits","regulatory_requirements","indian_vcs",
                     "accelerators_incubators","state_incentives",
                     "key_indian_markets","compliance_checklist", mode="before")
    @classmethod
    def coerce(cls, v): return _to_list(v)


class JudgeOutput(BaseModel):
    final_score:        int                      = 0
    verdict:            Literal["Proceed","Pivot","Abandon"] = "Pivot"
    summary:            str                      = ""
    recommendations:    List[str]               = []
    go_to_market:       str                      = ""
    action_plan_90_days:List[str]               = []
    key_metrics:        List[str]               = []
    scoring_breakdown:  Dict[str, Any]          = {}
    one_line_verdict:   str                      = ""

    @field_validator("final_score", mode="before")
    @classmethod
    def coerce_score(cls, v): return max(0, min(100, _to_int(v, 50)))

    @field_validator("verdict", mode="before")
    @classmethod
    def coerce_verdict(cls, v):
        if v in ("Proceed","Pivot","Abandon"): return v
        return "Pivot"

    @field_validator("recommendations","action_plan_90_days","key_metrics", mode="before")
    @classmethod
    def coerce(cls, v): return _to_list(v)

    @field_validator("scoring_breakdown", mode="before")
    @classmethod
    def coerce_bd(cls, v):
        if isinstance(v, dict): return v
        return {}


# ── API response models ────────────────────────────────────────────────────────
class SimulationResponse(BaseModel):
    status: Literal["success"] = "success"
    simulation_id: str

class SimulationSummary(BaseModel):
    id:          str
    idea:        str
    timestamp:   str
    final_score: int
    verdict:     str

class SimulationReport(BaseModel):
    id:           str
    idea:         str
    timestamp:    str
    status:       str             = "completed"
    founder:      FounderOutput   = Field(default_factory=FounderOutput)
    market:       MarketOutput    = Field(default_factory=MarketOutput)
    competitor:   CompetitorOutput = Field(default_factory=CompetitorOutput)
    customer:     CustomerOutput  = Field(default_factory=CustomerOutput)
    investor:     InvestorOutput  = Field(default_factory=InvestorOutput)
    failure:      FailureOutput   = Field(default_factory=FailureOutput)
    india_policy: IndiaPolicyOutput = Field(default_factory=IndiaPolicyOutput)
    judge:        JudgeOutput     = Field(default_factory=JudgeOutput)

class AskResponse(BaseModel):
    answer:       str
    sources_used: int = 0

class HistoryResponse(BaseModel):
    simulations: List[SimulationSummary]
    total:       int