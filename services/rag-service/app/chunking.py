from __future__ import annotations
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class Chunk:
    title: str
    source_id: str
    chunk_id: str
    text: str

    @property
    def snippet(self) -> str:
        t = self.text.strip().replace("\n", " ")
        return (t[:280] + "…") if len(t) > 280 else t


def chunk_markdown(doc_title: str, source_id: str, content: str) -> List[Chunk]:
    # Simple deterministic chunking: split by blank lines
    parts = [p.strip() for p in content.split("\n\n") if p.strip()]
    chunks: List[Chunk] = []
    for i, part in enumerate(parts):
        chunk_id = f"{source_id}#p{i}"
        chunks.append(Chunk(title=doc_title, source_id=source_id, chunk_id=chunk_id, text=part))
    return chunks
