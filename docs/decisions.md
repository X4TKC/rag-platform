# Decision log

Short records of why things are built this way. Interviewers ask "why", so each entry names the alternative.

## 2026-11-09: Local first, AWS second
Phase 1 runs entirely on the PC (kind + Ollama on a GTX 1080). AWS costs money per hour and needs a working card; everything except `terraform apply` can be built and checked without an account. On AWS the cluster is created for a session and destroyed after.

## 2026-11-09: Plain httpx instead of SDKs
`app/clients.py` calls the Ollama and Qdrant REST APIs directly. Every network call is in one readable file, and the image has fewer dependencies to scan. Alternative: `qdrant-client`, `ollama` packages; switch if the API surface used grows.

## 2026-11-09: Ollama outside the cluster
The model server runs on the host where the GPU is; the API reaches it at `host.docker.internal`. GPU passthrough into kind is possible but fragile on WSL2 and not the point of the project. On EKS it is replaced by Bedrock (managed, pay per token, no GPU nodes to run).

## 2026-11-09: Readiness vs liveness
`/healthz` only says the process is up, so Kubernetes does not restart the pod when Ollama is down (a restart would not fix it). `/readyz` checks the dependencies, so traffic stops while they are missing.

## 2026-11-09: Hardened pod defaults
Non-root user 10001, no privilege escalation, read-only root filesystem, memory limit. Cheap to do from the start and they are what security scanners (Trivy, Checkov, Kyverno) flag later.
