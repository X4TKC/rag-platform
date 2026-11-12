"""RAG API: ingest documents, then answer questions using only those documents.

Endpoints
  GET  /healthz   liveness: the process is up (Kubernetes restarts it if not)
  GET  /readyz    readiness: Ollama and Qdrant answer (no traffic until they do)
  POST /ingest    {"source": "name", "text": "..."} -> chunk, embed, store
  POST /ask       {"question": "..."} -> retrieve top chunks, ask the model
  GET  /metrics   Prometheus metrics (requests, latency, tokens of work)
"""

import time

from fastapi import FastAPI, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field

from app.chunking import chunk_text
from app.clients import Ollama, Qdrant
from app.config import settings

SYSTEM_PROMPT = (
    "Answer the question using only the context below. "
    "If the context does not contain the answer, say you don't know. "
    "Name the source of the facts you use."
)

REQUESTS = Counter("rag_requests_total", "Requests by endpoint and outcome", ["endpoint", "outcome"])
LATENCY = Histogram("rag_request_seconds", "Request latency", ["endpoint"])
CHUNKS = Counter("rag_chunks_ingested_total", "Chunks stored in the vector DB")

app = FastAPI(title="rag-platform")
llm = Ollama(settings.ollama_url, settings.chat_model, settings.embed_model)
store = Qdrant(settings.qdrant_url, settings.collection)


class IngestRequest(BaseModel):
    source: str = Field(min_length=1)
    text: str = Field(min_length=1)


class AskRequest(BaseModel):
    question: str = Field(min_length=1)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    deps = {"ollama": llm.ready(), "qdrant": store.ready()}
    if not all(deps.values()):
        raise HTTPException(503, detail=deps)
    return deps


@app.post("/ingest")
def ingest(req: IngestRequest):
    start = time.perf_counter()
    try:
        chunks = chunk_text(req.text, settings.chunk_chars)
        vectors = llm.embed(chunks)
        store.ensure_collection(len(vectors[0]))
        store.upsert(vectors, [{"source": req.source, "text": c} for c in chunks])
    except Exception:
        REQUESTS.labels("ingest", "error").inc()
        raise
    finally:
        LATENCY.labels("ingest").observe(time.perf_counter() - start)
    CHUNKS.inc(len(chunks))
    REQUESTS.labels("ingest", "ok").inc()
    return {"source": req.source, "chunks": len(chunks)}


@app.post("/ask")
def ask(req: AskRequest):
    start = time.perf_counter()
    try:
        [qvec] = llm.embed([req.question])
        hits = store.search(qvec, settings.top_k)
        if not hits:
            REQUESTS.labels("ask", "no_context").inc()
            return {"answer": "No documents ingested yet.", "sources": []}
        context = "\n\n".join(f"[{h['source']}]\n{h['text']}" for h in hits)
        answer = llm.chat(SYSTEM_PROMPT, f"Context:\n{context}\n\nQuestion: {req.question}")
    except Exception:
        REQUESTS.labels("ask", "error").inc()
        raise
    finally:
        LATENCY.labels("ask").observe(time.perf_counter() - start)
    REQUESTS.labels("ask", "ok").inc()
    return {
        "answer": answer,
        "sources": [{"source": h["source"], "score": round(h["score"], 3)} for h in hits],
    }


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
