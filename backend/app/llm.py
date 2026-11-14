"""Thin provider clients. Hosted = Anthropic Messages API; self-hosted = OpenAI-compatible (vLLM)."""
import time
import httpx
from .config import ANTHROPIC_API_KEY, SELF_HOSTED_URL, EMBEDDING_URL, EMBEDDING_MODEL, PRICING


def _cost(route: str, pt: int, ct: int) -> float:
    pin, pout = PRICING[route]
    return (pt * pin + ct * pout) / 1_000_000


def complete(route: str, model: str, system: str, user: str, max_tokens: int = 800) -> dict:
    t0 = time.time()
    if route == "hosted":
        r = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01"},
            json={"model": model, "max_tokens": max_tokens, "system": system,
                  "messages": [{"role": "user", "content": user}]},
            timeout=60,
        )
        r.raise_for_status()
        d = r.json()
        text = "".join(b.get("text", "") for b in d["content"])
        pt, ct = d["usage"]["input_tokens"], d["usage"]["output_tokens"]
    else:
        r = httpx.post(
            f"{SELF_HOSTED_URL}/chat/completions",
            json={"model": model, "max_tokens": max_tokens,
                  "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]},
            timeout=120,
        )
        r.raise_for_status()
        d = r.json()
        text = d["choices"][0]["message"]["content"]
        pt, ct = d["usage"]["prompt_tokens"], d["usage"]["completion_tokens"]
    return {"text": text, "prompt_tokens": pt, "completion_tokens": ct,
            "latency_ms": int((time.time() - t0) * 1000), "cost_usd": _cost(route, pt, ct)}


def embed(texts: list[str]) -> list[list[float]]:
    r = httpx.post(f"{EMBEDDING_URL}/embeddings",
                   json={"model": EMBEDDING_MODEL, "input": texts}, timeout=60)
    r.raise_for_status()
    return [x["embedding"] for x in r.json()["data"]]
