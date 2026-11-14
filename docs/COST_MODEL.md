# Cost model

Fill with your measured numbers (from the dashboard) — this document is a major interview asset.

| Item | Hosted API | Self-hosted (GPU) |
|---|---|---|
| Unit | $ / 1M tokens (in/out) | GPU $/hr ÷ tokens/hr at target utilisation |
| Fixed cost | none | GPU node(s), ops time |
| Break-even | — | monthly tokens where self-hosted < hosted |

**Break-even formula:** `monthly_gpu_cost / (hosted_price_per_token − self_hosted_marginal_cost)`.

Record: avg tokens/query, queries/day per tenant, GPU utilisation, router split (% self-hosted), and the resulting cost per 1k queries before/after routing.
