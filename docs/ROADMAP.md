# 6-week build roadmap

Goal: ship a repo + demo + write-ups that prove production AI engineering and architecture skill.

| Week | Build | Proof to publish |
|---|---|---|
| 1 | Docker stack, schema + RLS, FastAPI skeleton, tenant auth, ingestion (text/PDF), basic vector retrieval | Architecture diagram, ADR-0002 (tenancy model) |
| 2 | Hybrid search (vector + FTS + RRF), connectors (S3 + one SaaS source), incremental re-ingest | Ingestion pipeline doc; hit@5 baseline in README |
| 3 | Agent loop, risk-tiered tools, approval queue + minimal approval UI/endpoints, guardrails (prompt-injection filtering of retrieved text) | Threat-model doc (OWASP LLM Top 10 mapping) |
| 4 | Eval harness: golden set (50+ Qs per tenant), LLM-judge, CI gate; add reranker and measure delta | Eval results table v1→v3 in README |
| 5 | Hybrid router + self-hosted vLLM on GPU, cost model, dashboard (cost/latency/route) | ADR-0001 with real cost numbers; Medium post "Hybrid inference routing" |
| 6 | Terraform AWS + on-prem k3s notes, load test (k6/locust), 3-min demo video, polish README | LinkedIn launch post + Medium deep-dive + pinned repo |

## Definition of done per week
- Everything runs from `docker compose up`.
- One measurable number improves and is recorded in the README.
- One written decision (ADR) explains a trade-off.

## Stretch (pick 1–2)
- MCP server exposing the KB as a tool
- Per-tenant rate limits & budget caps with alerting
- Online evals from user thumbs up/down, feeding the golden set
- Semantic cache (Redis) with hit-rate metrics
- Fine-tuned small reranker — only if it beats the baseline in evals
