# Architecture

## Principles
1. **Tenant isolation in the database** (Postgres RLS), not only in app code.
2. **Measure before optimizing**: every change must move an eval or cost metric.
3. **Policy-driven routing**: data sensitivity decides where inference runs.
4. **Humans approve irreversible actions**.

## Components
- **Gateway (FastAPI)** — API-key/JWT auth → tenant context → rate/budget limits.
- **Ingestion** — connectors → chunk → embed → upsert; incremental via content hash.
- **Retriever** — pgvector (HNSW) + Postgres FTS fused with RRF; optional reranker.
- **Agent** — JSON action loop; tools tagged low/high risk; high-risk goes to `pending_actions`.
- **Router** — picks hosted API vs self-hosted vLLM (see ADR-0001).
- **Observability** — `llm_calls` table (tokens, latency, cost, route); extend with OpenTelemetry traces.
- **Evals** — golden datasets + LLM-judge; CI gate; results tracked in README.

## Deployment targets
| Target | Stack |
|---|---|
| Local | docker compose |
| AWS | ECS Fargate (API), RDS Postgres + pgvector, S3 ingest bucket, ALB, Secrets Manager (Terraform) |
| On-prem | k3s, Postgres, shared storage (Lustre/NFS) for model weights, vLLM on GPU nodes via NVIDIA device plugin |

## Security notes
- Treat retrieved text as untrusted (prompt-injection). Strip/flag instructions in chunks; never let retrieved text trigger high-risk tools without approval.
- Secrets via env/Secrets Manager; no keys in repo.
- RLS requires a non-owner DB role in production (see `db/schema.sql`).

## Scaling notes
- Stateless API → horizontal scale. Embedding/ingest workers scale separately.
- vLLM: continuous batching; size by tokens/sec per GPU; add autoscaling on queue depth.
