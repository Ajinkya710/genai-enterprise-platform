from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel, Field
from .rag import chat_with_citations

app = FastAPI(title="GenAI Enterprise Platform - RAG Service (Week 1)")

class ChatRequest(BaseModel):
    message: str = Field(min_length=1)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/chat")
def chat(req: ChatRequest):
    return chat_with_citations(req.message)
