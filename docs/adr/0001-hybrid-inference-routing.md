# ADR-0001: Hybrid inference routing (hosted API ↔ self-hosted vLLM)

**Status:** Accepted

## Context
Some tenants (e.g. universities, regulated clients) require data to stay on their network; others prefer best quality.
GPU capacity is a fixed cost; hosted APIs are variable cost.

## Decision
Route per request using a policy function: (1) restricted data / on-prem residency → self-hosted; (2) cheap tier + short low-stakes tasks → self-hosted; (3) otherwise hosted.

## Consequences
+ Meets data-residency needs; lowers cost on high-volume simple tasks.
− Two providers to operate; quality parity must be tracked in evals per route.
− Router rules need measurement: record route + eval score per route and revisit.

## Alternatives considered
- Hosted only: simplest, fails on-prem requirement.
- Self-hosted only: lower quality ceiling and heavier ops.
