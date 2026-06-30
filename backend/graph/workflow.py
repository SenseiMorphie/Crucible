"""
Parallel LangGraph pipeline with safe node wrappers.

Every node is wrapped in try/except — if an agent fails for any reason,
it returns empty dict for its field and the pipeline continues.
The Judge agent always runs and always returns a verdict.

Pipeline:
  START → Founder → Market → [Competitor ‖ Customer ‖ IndiaPolicy]
       → [Investor ‖ Failure] → Judge → END
"""
from langgraph.graph import StateGraph, START, END
from backend.graph.state import StartupState, initial_state

from backend.agents.founder      import founder_node
from backend.agents.market       import market_node
from backend.agents.competitor   import competitor_node
from backend.agents.customer     import customer_node
from backend.agents.investor     import investor_node
from backend.agents.failure      import failure_node
from backend.agents.india_policy import india_policy_node
from backend.agents.judge        import judge_node


def _safe(name: str, fn):
    """Wrap an agent node so it never raises — logs error and returns empty update."""
    def wrapper(state: dict) -> dict:
        try:
            return fn(state)
        except Exception as e:
            print(f"\n⚠️  {name} agent error (pipeline continues): {e}\n", flush=True)
            # Return empty dict for the agent's key so state stays valid
            key_map = {
                "Founder":     "founder",
                "Market":      "market",
                "Competitor":  "competitor",
                "Customer":    "customer",
                "Investor":    "investor",
                "Failure":     "failure",
                "IndiaPolicy": "india_policy",
                "Judge":       "judge",
            }
            return {key_map.get(name, name.lower()): {}}
    return wrapper


def _build():
    g = StateGraph(StartupState)

    # Register all nodes with safe wrappers
    g.add_node("Founder",     _safe("Founder",     founder_node))
    g.add_node("Market",      _safe("Market",      market_node))
    g.add_node("Competitor",  _safe("Competitor",  competitor_node))
    g.add_node("Customer",    _safe("Customer",    customer_node))
    g.add_node("IndiaPolicy", _safe("IndiaPolicy", india_policy_node))
    g.add_node("Investor",    _safe("Investor",    investor_node))
    g.add_node("Failure",     _safe("Failure",     failure_node))
    g.add_node("Judge",       _safe("Judge",       judge_node))

    # Sequential start
    g.add_edge(START,     "Founder")
    g.add_edge("Founder", "Market")

    # Fan-out: Market → 3 parallel agents
    g.add_edge("Market", "Competitor")
    g.add_edge("Market", "Customer")
    g.add_edge("Market", "IndiaPolicy")

    # Fan-in: [Competitor + Customer] → [Investor + Failure] (parallel)
    g.add_edge("Competitor", "Investor")
    g.add_edge("Customer",   "Investor")
    g.add_edge("Competitor", "Failure")
    g.add_edge("Customer",   "Failure")

    # Fan-in: [Investor + Failure + IndiaPolicy] → Judge
    g.add_edge("Investor",    "Judge")
    g.add_edge("Failure",     "Judge")
    g.add_edge("IndiaPolicy", "Judge")

    g.add_edge("Judge", END)
    return g.compile()


_workflow = _build()


def run_simulation(idea: str) -> StartupState:
    print(f"\n{'#'*60}")
    print(f"# SIMULATION START")
    print(f"# {idea[:55]}")
    print(f"# Pipeline: Founder→Market→[Competitor‖Customer‖India]→[Investor‖Failure]→Judge")
    print(f"{'#'*60}", flush=True)
    return _workflow.invoke(initial_state(idea))
