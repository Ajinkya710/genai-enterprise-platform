from __future__ import annotations
import os
import time
from typing import Any, Dict, List
from dotenv import load_dotenv
from openai import OpenAI

from .chunking import Chunk, chunk_markdown
from .retrieval import retrieve_top_k

load_dotenv()

client = OpenAI()  # reads OPENAI_API_KEY from env

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
SEED_DOCS_DIR = os.getenv("SEED_DOCS_DIR", "../../eval/datasets/seed_docs")
TOP_K = int(os.getenv("TOP_K", "5"))


def load_seed_chunks() -> List[Chunk]:
    chunks: List[Chunk] = []
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), SEED_DOCS_DIR))
    for fname in os.listdir(base):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(base, fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        title = fname.replace("_", " ").replace(".md", "").title()
        chunks.extend(chunk_markdown(doc_title=title, source_id=fname, content=content))
    return chunks


SEED_CHUNKS = load_seed_chunks()


def estimate_cost_placeholder() -> float:
    # Week 1: placeholder. We'll make this real in Week 3/7.
    return 0.0


def chat_with_citations(message: str) -> Dict[str, Any]:
    t0 = time.time()

    top = retrieve_top_k(SEED_CHUNKS, message, k=TOP_K)
    top_chunks = [c for (c, _s) in top]

    context_blocks = "\n\n".join(
        [f"[{c.chunk_id}] {c.text.strip()}" for c in top_chunks]
    )

    system_rules = (
        "You are an enterprise assistant.\n"
        "Answer ONLY using the provided CONTEXT.\n"
        "If the answer is not in the context, say: \"I don't know based on the provided documents.\".\n"
        "When you use a fact, cite it inline using the chunk id in square brackets, e.g. [file.md#p2].\n"
        "Keep the answer concise and actionable.\n"
    )

    user_prompt = (
        f"QUESTION:\n{message}\n\n"
        f"CONTEXT:\n{context_blocks}\n"
    )

    # Responses API call
    res = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": system_rules},
            {"role": "user", "content": user_prompt},
        ],
    )

    # Extract text output (safe approach)
    answer_text = ""
    for item in getattr(res, "output", []) or []:
        if getattr(item, "type", None) == "message":
            for c in getattr(item, "content", []) or []:
                if getattr(c, "type", None) in ("output_text", "text"):
                    answer_text += getattr(c, "text", "")

    latency_ms = int((time.time() - t0) * 1000)

    citations = [
        {
            "title": c.title,
            "source_id": c.source_id,
            "chunk_id": c.chunk_id,
            "snippet": c.snippet,
        }
        for c in top_chunks[: max(2, min(5, len(top_chunks)))]
    ]

    return {
        "answer": answer_text.strip() or "No answer generated.",
        "citations": citations,
        "latency_ms": latency_ms,
        "cost_estimate": estimate_cost_placeholder(),
    }
