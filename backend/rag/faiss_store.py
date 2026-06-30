"""Optional FAISS index — fails silently if unavailable."""
from __future__ import annotations
from pathlib import Path
import sys

from backend.config import FAISS_DIR
from backend.rag.chroma_store import _flatten, _get_embedder


def save_faiss_index(sim_id: str, report: dict) -> bool:
    try:
        from langchain_community.vectorstores import FAISS
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        text   = _flatten(report)
        chunks = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=60).split_text(text)
        index  = FAISS.from_texts(chunks, _get_embedder())
        path   = Path(FAISS_DIR) / sim_id
        path.mkdir(parents=True, exist_ok=True)
        index.save_local(str(path))
        return True
    except Exception as e:
        print(f"   [FAISS] Skipped: {e}", file=sys.stderr)
        return False
