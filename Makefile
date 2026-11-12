# Every command the project uses, in one place. `make help` lists them.
CLUSTER := rag
IMAGE   := rag-api:dev

help:            ## list targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/'

test:            ## unit tests (no Docker needed)
	.venv/bin/python -m pytest -q

up:              ## kind cluster + qdrant + the API via Helm
	kind create cluster --config deploy/kind/cluster.yaml || true
	docker build -t $(IMAGE) .
	kind load docker-image $(IMAGE) --name $(CLUSTER)
	kubectl apply -f deploy/qdrant.yaml
	helm upgrade --install rag-api deploy/helm/rag-api --wait

down:            ## delete the whole cluster
	kind delete cluster --name $(CLUSTER)

ollama:          ## run Ollama in Docker on port 11434 and pull the two models
	docker start ollama 2>/dev/null || docker run -d --name ollama -p 11434:11434 \
	  -v ollama:/root/.ollama --restart unless-stopped ollama/ollama:latest
	docker exec ollama ollama pull nomic-embed-text
	docker exec ollama ollama pull llama3.2:3b

demo:            ## ingest the sample docs and ask a question
	for f in sample-docs/*.md; do \
	  jq -Rs --arg s "$$(basename $$f)" '{source:$$s, text:.}' $$f | \
	  curl -s -X POST localhost:8080/ingest -H 'content-type: application/json' -d @-; echo; \
	done
	curl -s -X POST localhost:8080/ask -H 'content-type: application/json' \
	  -d '{"question":"How do I roll back a bad deploy?"}' | jq

.PHONY: help test up down ollama demo
