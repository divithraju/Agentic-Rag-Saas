# Evaluation strategy

- **Golden sets** per tenant (`evals/golden/*.jsonl`): question, expected source, must-include facts.
- **Metrics**: retrieval hit@k, answer correctness (contains / judge), groundedness (judge), latency, cost.
- **Judge hygiene**: calibrate the LLM judge against ~30 human-labelled examples; report agreement.
- **CI gate**: thresholds in `evals/run_evals.py`; PRs that regress fail.
- **Online loop**: log thumbs up/down → review → promote failures into the golden set.
- **Known limits**: judge bias toward verbose answers; small golden sets are noisy — report n and confidence.
