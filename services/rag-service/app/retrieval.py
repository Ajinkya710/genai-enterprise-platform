from __future__ import annotations
import re
from typing import List, Tuple
from .chunking import Chunk

STOPWORDS = {
    "the","a","an","and","or","to","of","in","on","for","with","as","by","is","are","was","were",
    "be","been","it","this","that","these","those","at","from","into","over","under","about"
}

def tokenize(text: str) -> List[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]

def score_chunk(query_tokens: List[str], chunk: Chunk) -> int:
    chunk_tokens = set(tokenize(chunk.text))
    return sum(1 for t in query_tokens if t in chunk_tokens)

def retrieve_top_k(chunks: List[Chunk], query: str, k: int = 5) -> List[Tuple[Chunk, int]]:
    q = tokenize(query)
    scored = [(c, score_chunk(q, c)) for c in chunks]
    scored.sort(key=lambda x: x[1], reverse=True)
    # keep only meaningful matches, but ensure at least 2 if anything exists
    filtered = [(c,s) for (c,s) in scored if s > 0]
    if len(filtered) >= 2:
        return filtered[:k]
    # fallback: return top k even if 0 score (so system never breaks)
    return scored[:k]
