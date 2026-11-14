import json
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from . import agent, rag
from .config import API_KEYS
from .db import tenant_conn
from .llm import complete
from .router import choose_route

app = FastAPI(title="Agentic RAG SaaS")


def tenant_from_key(x_api_key: str | None) -> str:
    t = API_KEYS.get(x_api_key or "")
    if not t:
        raise HTTPException(401, "invalid API key")
    return t


class IngestReq(BaseModel):
    source: str
    text: str
    sensitivity: str = "normal"


class ChatReq(BaseModel):
    question: str
    max_steps: int = 3


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/v1/ingest")
def ingest(req: IngestReq, x_api_key: str | None = Header(None)):
    tenant = tenant_from_key(x_api_key)
    return {"chunks": rag.ingest(tenant, req.source, req.text, req.sensitivity)}


@app.post("/v1/chat")
def chat(req: ChatReq, x_api_key: str | None = Header(None)):
    tenant = tenant_from_key(x_api_key)
    with tenant_conn(tenant) as conn:
        policy = conn.execute("SELECT policy FROM tenants WHERE id=%s", (tenant,)).fetchone()
    policy = policy[0] if policy else {}

    context = rag.retrieve(tenant, req.question)
    sensitivity = "restricted" if any(c["sensitivity"] == "restricted" for c in context) else "normal"
    scratch = f"Question: {req.question}\nContext:\n" + "\n---\n".join(
        f"[{c['source']}] {c['content']}" for c in context)

    final, steps = None, []
    for _ in range(req.max_steps):
        route = choose_route(policy, sensitivity, prompt_tokens=len(scratch) // 4)
        out = complete(route.backend, route.model, agent.SYSTEM, scratch)
        with tenant_conn(tenant) as conn:
            conn.execute(
                """INSERT INTO llm_calls (tenant_id, route, model, reason, prompt_tokens, completion_tokens,
                   latency_ms, cost_usd) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                (tenant, route.backend, route.model, route.reason, out["prompt_tokens"],
                 out["completion_tokens"], out["latency_ms"], out["cost_usd"]))
        act = agent.parse_action(out["text"])
        if "final" in act:
            final = act
            break
        result = agent.run_tool(tenant, act.get("action", ""), act.get("args", {}))
        steps.append({"action": act, "result": result})
        scratch += f"\nTool {act.get('action')} result: {json.dumps(result, default=str)[:2000]}"
    return {"answer": (final or {}).get("final", "No answer produced"),
            "citations": (final or {}).get("citations", []),
            "retrieved_sources": [c["source"] for c in context],
            "route": route.backend, "steps": steps}
