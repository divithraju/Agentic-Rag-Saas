"""Golden-set eval runner. Exits non-zero if quality drops below thresholds (used as a CI gate).
Metrics: retrieval hit@k (expected source retrieved), answer-contains check, and LLM-as-judge groundedness."""
import json, os, sys, time, pathlib, httpx

API = os.getenv("API_URL", "http://localhost:8000")
THRESH = {"hit_rate": 0.80, "contains_rate": 0.75, "groundedness": 0.80}
ROOT = pathlib.Path(__file__).parent


def judge(question: str, answer: str, sources: list[str]) -> float:
    """LLM-as-judge via the platform's own hosted model. Replace with a stronger independent judge if possible."""
    r = httpx.post("https://api.anthropic.com/v1/messages",
        headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"},
        json={"model": os.getenv("JUDGE_MODEL", "claude-sonnet-5-5"), "max_tokens": 20,
              "messages": [{"role": "user", "content":
                f"Question: {question}\nAnswer: {answer}\nCited sources: {sources}\n"
                "Score 1 if the answer is supported by the cited sources and does not invent facts, else 0. "
                "Reply with just 0 or 1."}]}, timeout=60)
    r.raise_for_status()
    return 1.0 if r.json()["content"][0]["text"].strip().startswith("1") else 0.0


def main():
    rows = [json.loads(l) for l in (ROOT / "golden/sample.jsonl").read_text().splitlines() if l.strip()]
    hits = contains = ground = 0.0
    lat = []
    for row in rows:
        t0 = time.time()
        r = httpx.post(f"{API}/v1/chat", headers={"x-api-key": row["tenant_key"]},
                       json={"question": row["question"]}, timeout=120).json()
        lat.append((time.time() - t0) * 1000)
        hits += row["expected_source"] in r["retrieved_sources"]
        contains += all(s.lower() in r["answer"].lower() for s in row["must_include"])
        ground += judge(row["question"], r["answer"], r["citations"])
    n = len(rows)
    res = {"n": n, "hit_rate": hits / n, "contains_rate": contains / n, "groundedness": ground / n,
           "avg_latency_ms": sum(lat) / n}
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results/latest.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))
    failed = [k for k, v in THRESH.items() if res[k] < v]
    if failed:
        print("EVAL GATE FAILED:", failed)
        sys.exit(1)


if __name__ == "__main__":
    main()
