"""Thin HTTP clients for Ollama (embeddings + chat) and Qdrant (vector store).

Plain httpx calls instead of SDKs, so every request the service makes is
visible in this one file. Later a Bedrock client can implement the same
two methods (embed, chat) and be selected by config.
"""

import uuid

import httpx


class Ollama:
    def __init__(self, base_url: str, chat_model: str, embed_model: str):
        self.http = httpx.Client(base_url=base_url, timeout=120)
        self.chat_model = chat_model
        self.embed_model = embed_model

    def embed(self, texts: list[str]) -> list[list[float]]:
        r = self.http.post("/api/embed", json={"model": self.embed_model, "input": texts})
        r.raise_for_status()
        return r.json()["embeddings"]

    def chat(self, system: str, user: str) -> str:
        r = self.http.post("/api/chat", json={
            "model": self.chat_model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        })
        r.raise_for_status()
        return r.json()["message"]["content"]

    def ready(self) -> bool:
        try:
            return self.http.get("/api/tags", timeout=3).status_code == 200
        except httpx.HTTPError:
            return False


class Qdrant:
    def __init__(self, base_url: str, collection: str):
        self.http = httpx.Client(base_url=base_url, timeout=30)
        self.collection = collection

    def ensure_collection(self, dim: int) -> None:
        """Create the collection on first use (cosine distance)."""
        if self.http.get(f"/collections/{self.collection}").status_code == 200:
            return
        r = self.http.put(f"/collections/{self.collection}", json={
            "vectors": {"size": dim, "distance": "Cosine"},
        })
        r.raise_for_status()

    def upsert(self, vectors: list[list[float]], payloads: list[dict]) -> None:
        points = [
            {"id": str(uuid.uuid4()), "vector": v, "payload": p}
            for v, p in zip(vectors, payloads)
        ]
        r = self.http.put(
            f"/collections/{self.collection}/points",
            params={"wait": "true"},
            json={"points": points},
        )
        r.raise_for_status()

    def search(self, vector: list[float], limit: int) -> list[dict]:
        r = self.http.post(f"/collections/{self.collection}/points/search", json={
            "vector": vector, "limit": limit, "with_payload": True,
        })
        if r.status_code == 404:  # nothing ingested yet
            return []
        r.raise_for_status()
        return [{"score": hit["score"], **hit["payload"]} for hit in r.json()["result"]]

    def ready(self) -> bool:
        try:
            return self.http.get("/readyz", timeout=3).status_code == 200
        except httpx.HTTPError:
            return False
