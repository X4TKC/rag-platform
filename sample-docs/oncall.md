# On-call notes (sample)

The API exposes Prometheus metrics at /metrics. The main alert fires when the error rate of /ask is above 5% for 10 minutes.

Most errors come from the model server being down. Check /readyz: it reports whether Ollama and Qdrant respond.

Costs: the AWS environment is created with Terraform for a session and destroyed after. A budget alarm emails at $10 per month.
