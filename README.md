# rag-platform

[![ci](https://github.com/X4TKC/rag-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/X4TKC/rag-platform/actions/workflows/ci.yml)

A question-answering API over your own documents (RAG: retrieval-augmented generation), built as a **platform engineering portfolio project**. The app is deliberately small. The interesting part is everything around it: containers, Kubernetes, Helm, then Terraform on AWS, CI/CD with security scanning, monitoring and cost control.

```
            POST /ingest                         POST /ask
 docs ──► chunk ──► embed (Ollama) ──► Qdrant ◄── embed question
                                                  │ top 4 chunks
                                                  ▼
                                    chat model (Ollama) ──► answer + sources
```

## Roadmap

| Phase | What | Cost | Status |
|---|---|---|---|
| 1 | App, Docker, kind cluster, Helm chart, unit tests | free | **done**: runs on kind, end-to-end demo passes |
| 2 | Terraform: VPC, EKS, ECR, IRSA; Bedrock instead of Ollama; apply → demo → destroy | ~$1 per session | planned |
| 3 | GitHub Actions: tests, Helm lint, Trivy image scan, kind end-to-end test; later Checkov on Terraform, OIDC to AWS (no keys) | free | **in progress** |
| 4 | Prometheus + Grafana dashboards, alerts, AWS Budgets / OpenCost | free locally | planned |
| 5 | Architecture diagram, decision log, write-up | free | ongoing (`docs/decisions.md`) |

## Layout

```
app/
  main.py        API endpoints + Prometheus metrics
  clients.py     HTTP calls to Ollama and Qdrant (no SDKs, everything visible)
  chunking.py    split documents into ~800-char chunks
  config.py      all settings from environment variables
tests/           unit tests with fake Ollama/Qdrant
Dockerfile       slim image, non-root user
docker-compose.yml  quickest local run, no Kubernetes
deploy/
  kind/cluster.yaml   local 2-node Kubernetes cluster
  qdrant.yaml         vector DB StatefulSet + volume
  helm/rag-api/       Helm chart for the API
sample-docs/     two small docs for the demo
docs/decisions.md    why things are the way they are
.github/workflows/ci.yml  tests, Helm lint, Trivy scan, kind end-to-end test
```

## Run it

**Unit tests** (only Python needed):
```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
make test
```

**With Docker Compose** (needs Docker Desktop with WSL integration on):
```sh
docker compose up -d --build
docker compose exec ollama ollama pull llama3.2:3b
docker compose exec ollama ollama pull nomic-embed-text
# API on localhost:8000, try: curl localhost:8000/readyz
```

**On Kubernetes (kind)** (also needs kind, kubectl, helm, jq):
```sh
make ollama   # Ollama in Docker + the two models (~2.3 GB, once)
make up       # cluster + qdrant + API, ~2 min
make demo     # ingest sample-docs/, ask a question
make down     # delete everything
```

## API

| Method | Path | Body | Returns |
|---|---|---|---|
| GET | `/healthz` | | process alive |
| GET | `/readyz` | | 503 until Ollama and Qdrant respond |
| POST | `/ingest` | `{"source": "x.md", "text": "..."}` | number of chunks stored |
| POST | `/ask` | `{"question": "..."}` | answer + sources with scores |
| GET | `/metrics` | | Prometheus metrics |
