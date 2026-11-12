# rag-platform: notes for Claude

Portfolio project for the user's DevOps / AI-platform job search. **The user must be able to explain every file in an interview.** Keep code small and commented on the *why*; prefer one obvious way over clever abstractions. Add an entry to `docs/decisions.md` for every non-obvious choice.

- Phases and status: README roadmap table. Update it when a phase moves.
- `make test` runs unit tests with fakes; no Docker needed. Python 3.14 venv in `.venv`.
- As of 2026-11-09: Docker Desktop is installed on Windows but WSL integration is off (`docker` not found in WSL). kind, kubectl, helm, terraform, gh, aws CLI are not installed yet. Ask before installing.
- No personal AWS account yet (old one has an unpaid ~$1 balance, Bolivian card issues). Never use the user's employer (Digital Harbor) AWS accounts for this.
- Untested assumption: pods in kind reach the host's Ollama via `host.docker.internal` (Docker Desktop). Verify on first `make up`.

## History
| Date | Change |
|---|---|
| 2026-11-09 | Phase 1 scaffold: FastAPI app (ingest/ask/health/metrics), httpx clients, chunking, 6 unit tests passing; Dockerfile, compose, kind config, Qdrant StatefulSet, Helm chart, Makefile, sample docs, decision log. Not yet run in Docker/kind |
