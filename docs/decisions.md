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

## 2026-11-12: Ollama on CPU, in Docker
Current Ollama builds no longer include CUDA kernels for the GTX 1080 (compute capability 6.1), so the model runs on the Ryzen CPU. A 3B model answers in about 6 s, which is fine for a demo. Ollama runs as a Docker container (`make ollama`) so the setup is the same on any machine; kind pods reach it through `host.docker.internal` (Docker Desktop). On a Linux CI runner that name does not exist, so CI puts Ollama on kind's Docker network and passes its IP to Helm.

## 2026-11-12: Actions pinned to commit SHAs
In March 2026 attackers rewrote most tags of `aquasecurity/trivy-action` and published a malicious Trivy v0.69.4 (CVE-2026-33634); workflows using `@v0.x` tags ran the stealer. Tags are mutable, commit SHAs are not, so every action in CI is pinned to a full SHA with the version in a comment, and the Trivy binary is pinned to v0.69.3. Dependabot can bump the SHAs later.

## 2026-11-12: Small model in CI
The end-to-end job uses `qwen2.5:0.5b` instead of `llama3.2:3b`: it downloads in seconds and runs on the 4-CPU runner. The job checks the plumbing (cluster, chart, networking, retrieval), not answer quality, so it asserts that the right source document is retrieved rather than the exact answer text.

## 2026-11-20: Multi-stage image without pip
The first CI run failed the Trivy gate: 1 HIGH in Debian's zlib and 5 HIGH in packages bundled with the base image's pip (msgpack, urllib3, setuptools). None were in the app's own dependencies. The image now installs dependencies into a venv in a build stage, removes pip/setuptools from the final stage (the app never installs anything at runtime), and runs `apt-get upgrade` for Debian security fixes. Result: 0 fixable HIGH/CRITICAL. Alternative: `.trivyignore` the findings, rejected because they were fixable.
