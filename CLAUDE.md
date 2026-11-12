# rag-platform: notes for Claude

Portfolio project (DevOps / AI platform). **The author must be able to explain every file in an interview.** Keep code small and commented on the *why*; prefer one obvious way over clever abstractions. Add an entry to `docs/decisions.md` for every non-obvious choice.

- Phases and status: README roadmap table. Update it when a phase moves.
- `make test` runs unit tests with fakes; no Docker needed. Python 3.14 venv in `.venv`.
- Tools (2026-11-12): Docker Desktop with WSL integration for Ubuntu; kind, kubectl, helm, gh, jq in `~/.local/bin`. GitHub account X4TKC (gh logged in). Ollama runs as Docker container `ollama` on CPU (GTX 1080 unsupported by current Ollama CUDA builds).
- Local loop: `make ollama` (once), `make up`, `make demo`, `make down`. During heavy load the kind controller-manager can lose leader election and restart; it recovers by itself.
- No AWS account connected yet: phase 2 is written and checked without one first. Only ever use a personal AWS account for this project, never an employer's.
- Pods in kind reach the host's Ollama via `host.docker.internal` (verified 2026-11-12). CI passes the Ollama container IP instead.
- CI actions pinned to full commit SHAs (Trivy tag hijack, March 2026); keep it that way.

## History
| Date | Change |
|---|---|
| 2026-11-12 | First real run on kind: ingest + ask works (6 s on CPU). Added `make ollama`, CI workflow (pytest, helm lint, Trivy, kind e2e with qwen2.5:0.5b), decisions on CPU Ollama and SHA pinning |
| 2026-11-09 | Phase 1 scaffold: FastAPI app (ingest/ask/health/metrics), httpx clients, chunking, 6 unit tests passing; Dockerfile, compose, kind config, Qdrant StatefulSet, Helm chart, Makefile, sample docs, decision log. Not yet run in Docker/kind |
