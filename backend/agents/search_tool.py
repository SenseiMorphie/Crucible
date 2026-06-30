from __future__ import annotations
import sys, time
from typing import List, Dict
import backend.config as cfg


def _search(query: str, n: int = 3) -> List[Dict]:
    try:
        from duckduckgo_search import DDGS
        with DDGS() as d:
            results = list(d.text(query, max_results=n))
        time.sleep(0.5)
        return [{"title": r.get("title",""), "snippet": r.get("body","")[:400]} for r in results]
    except Exception as e:
        print(f"      -> Search failed: {e}", file=sys.stderr)
        return []


def _fmt(results: List[Dict], cap: int = 1800) -> str:
    if not results: return ""
    out, total = [], 0
    for i, r in enumerate(results, 1):
        entry = f"[{i}] {r['title']}\n{r['snippet']}"
        if total + len(entry) > cap: break
        out.append(entry); total += len(entry)
    return "\n\n".join(out)


def run_searches(queries: List[str]) -> str:
    if not cfg.USE_WEB_SEARCH: return ""
    all_res: List[Dict] = []
    for q in queries[:2]:
        print(f"      -> Searching: {q[:60]}", flush=True)
        all_res.extend(_search(q, n=3))
        if len(all_res) >= 6: break
    out = _fmt(all_res)
    print(f"      -> {str(len(all_res)) + ' results' if out else 'No results'}", flush=True)
    return out
