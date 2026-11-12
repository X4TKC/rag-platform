# Deploy runbook (sample)

Deploys go through the CI pipeline. Merging to main builds the image, scans it with Trivy and pushes it to the registry. Helm then upgrades the release in the target environment.

To roll back a bad deploy, run `helm history rag-api` to find the last good revision, then `helm rollback rag-api <revision>`. Check that the pods become ready with `kubectl get pods -w`.

If the readiness probe fails after a deploy, the old pods keep serving traffic, so users are not affected. Look at `kubectl describe pod` and the logs before rolling back.
