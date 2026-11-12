"""Unit tests: no Ollama or Qdrant needed, both are replaced by fakes."""

from fastapi.testclient import TestClient

import app.main as main
from app.chunking import chunk_text


class FakeLLM:
    def embed(self, texts):
        # 3-dim "embedding": crude but deterministic
        return [[len(t), t.count("a"), 1.0] for t in texts]

    def chat(self, system, user):
        assert "Context:" in user
        return "fake answer"

    def ready(self):
        return True


class FakeStore:
    def __init__(self):
        self.points = []

    def ensure_collection(self, dim):
        self.dim = dim

    def upsert(self, vectors, payloads):
        self.points += payloads

    def search(self, vector, limit):
        return [{"score": 0.9, **p} for p in self.points[:limit]]

    def ready(self):
        return True


def client():
    main.llm = FakeLLM()
    main.store = FakeStore()
    return TestClient(main.app)


def test_chunking_respects_limit():
    text = "\n\n".join(["word " * 50] * 10)  # ten 250-char paragraphs
    chunks = chunk_text(text, 600)
    assert all(len(c) <= 600 for c in chunks)
    assert len(chunks) == 5  # two paragraphs per chunk


def test_chunking_splits_huge_paragraph():
    assert [len(c) for c in chunk_text("x" * 2000, 800)] == [800, 800, 400]


def test_ask_before_ingest():
    r = client().post("/ask", json={"question": "anything?"})
    assert r.json()["sources"] == []


def test_ingest_then_ask():
    c = client()
    r = c.post("/ingest", json={"source": "notes.md", "text": "Para one.\n\nPara two."})
    assert r.status_code == 200 and r.json()["chunks"] == 1
    r = c.post("/ask", json={"question": "what?"})
    assert r.json()["answer"] == "fake answer"
    assert r.json()["sources"][0]["source"] == "notes.md"


def test_validation_rejects_empty():
    assert client().post("/ask", json={"question": ""}).status_code == 422


def test_metrics_exposed():
    c = client()
    c.get("/healthz")
    assert "rag_requests_total" in c.get("/metrics").text
