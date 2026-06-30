"""
Core LLM utilities.
call_llm() NEVER raises — it returns {} on failure so no agent ever crashes the pipeline.
"""
from __future__ import annotations
import json, re, sys
from typing import Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import backend.config as cfg


def get_llm(temperature: float = 0.2) -> ChatOpenAI:
    if cfg.LLM_PROVIDER == "ollama":
        return ChatOpenAI(model=cfg.OLLAMA_MODEL,
                          base_url=f"{cfg.OLLAMA_BASE_URL}/v1",
                          api_key="ollama", temperature=temperature)
    if not cfg.OPENROUTER_API_KEY or "REPLACE" in cfg.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set in .env")
    return ChatOpenAI(
        model=cfg.OPENROUTER_MODEL,
        base_url=cfg.OPENROUTER_BASE_URL,
        api_key=cfg.OPENROUTER_API_KEY,
        temperature=temperature,
        default_headers={"HTTP-Referer": "http://localhost:8000",
                         "X-Title": "Startup Simulator"},
    )


def extract_json(text: str) -> dict[str, Any]:
    """Try multiple strategies to get JSON out of any LLM response."""
    if not text:
        return {}
    text = text.strip()
    # 1. ```json block
    m = re.search(r"```json\s*([\s\S]*?)\s*```", text)
    if m:
        try: return json.loads(m.group(1))
        except: pass
    # 2. any ``` block
    m = re.search(r"```\s*([\s\S]*?)\s*```", text)
    if m:
        try: return json.loads(m.group(1))
        except: pass
    # 3. find outermost { }
    start = text.find("{")
    end   = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try: return json.loads(text[start:end+1])
        except: pass
    # 4. whole text
    try: return json.loads(text)
    except: return {}


def call_llm(system_prompt: str, temperature: float = 0.2, max_retries: int = 2) -> dict[str, Any]:
    """
    Call LLM with system_prompt. Returns parsed JSON dict.
    NEVER raises — returns {} on any failure so the pipeline keeps running.
    """
    try:
        llm = get_llm(temperature=temperature)
    except Exception as e:
        print(f"      → ❌ LLM init failed: {e}", flush=True)
        return {}

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=(
            "Respond with ONLY a valid JSON object. "
            "Start your response with { and end with }. "
            "No explanation, no markdown, no text outside the JSON."
        )),
    ]

    for attempt in range(max_retries + 1):
        try:
            print(f"      → LLM call (attempt {attempt+1}/{max_retries+1})...", flush=True)
            response = llm.invoke(messages)
            result   = extract_json(response.content)
            if result:
                print(f"      → ✅ Got {len(result)} keys", flush=True)
                return result
            else:
                print(f"      → ⚠️  No JSON found. Preview: {response.content[:200]}", flush=True)
        except Exception as e:
            print(f"      → ❌ Attempt {attempt+1} failed: {e}", flush=True)

    print("      → ⚠️  All attempts failed — returning empty dict", flush=True)
    return {}


def truncate(text: str, max_chars: int = 200) -> str:
    """Truncate a string for use in prompts to avoid token overflow."""
    if not text:
        return ""
    return text[:max_chars] + ("..." if len(text) > max_chars else "")


def top(items: list, n: int = 3, max_chars: int = 150) -> str:
    """Take first n items from a list and join as a short string for prompts."""
    if not items:
        return "none"
    return " | ".join(truncate(str(i), max_chars) for i in items[:n])
