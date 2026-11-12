"""All settings come from environment variables, so the same image runs
on a laptop, in kind and later on EKS. Only the values change."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    collection: str = os.getenv("COLLECTION", "docs")
    chat_model: str = os.getenv("CHAT_MODEL", "llama3.2:3b")
    embed_model: str = os.getenv("EMBED_MODEL", "nomic-embed-text")
    top_k: int = int(os.getenv("TOP_K", "4"))
    chunk_chars: int = int(os.getenv("CHUNK_CHARS", "800"))


settings = Settings()
