from __future__ import annotations
from langchain_core.messages import SystemMessage, HumanMessage
from backend.agents.base import get_llm
from backend.rag.chroma_store import retrieve_chunks, _flatten
from backend.utils.storage import load_simulation


def answer_question(sim_id: str, question: str) -> tuple[str, int]:
    """
    Answer a question about a simulation report using RAG.
    Falls back to using the full report text if ChromaDB retrieval returns nothing.
    Returns (answer_text, num_chunks_used).
    """
    # Try ChromaDB first
    chunks = retrieve_chunks(sim_id, question, k=5)

    if chunks:
        context = "\n\n---\n\n".join(chunks)
        source = "ChromaDB retrieval"
        n = len(chunks)
    else:
        # Fallback: load full report and use it directly
        print(f"   [QA] ChromaDB returned no chunks — falling back to full report text", flush=True)
        report = load_simulation(sim_id)
        if not report:
            return "Could not find the simulation report. Please re-run the simulation.", 0
        context = _flatten(report)[:6000]  # cap to avoid token overflow
        source = "full report text"
        n = 1

    print(f"   [QA] Answering with {source} ({n} sources)", flush=True)

    prompt = f"""You are a helpful startup analyst assistant.
Answer the user's question using ONLY the information in the context below (from a startup simulation report).
Be specific, concrete, and cite actual data from the context.
If the answer is not in the context, say so clearly.

CONTEXT:
{context}"""

    llm = get_llm(temperature=0.2)
    response = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=question),
    ])
    return response.content, n
