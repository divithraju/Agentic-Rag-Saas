"""Small, provider-agnostic agent loop: the model emits JSON actions; tools are risk-tiered."""
import json
from .db import tenant_conn
from .rag import retrieve

SYSTEM = """You are an enterprise assistant. Answer ONLY from the provided context or tool results.
If the context is insufficient, say so. Respond with JSON only:
{"action": "<tool name>", "args": {...}}  OR  {"final": "<answer>", "citations": ["<source>", ...]}"""

# risk: low = auto-run, high = requires human approval before execution
TOOLS = {
    "search_kb": {"risk": "low", "fn": lambda tenant, args: retrieve(tenant, args["query"])},
    "create_ticket": {"risk": "high", "fn": None},   # example high-risk action → approval queue
}


def run_tool(tenant_id: str, name: str, args: dict) -> dict:
    tool = TOOLS.get(name)
    if not tool:
        return {"error": f"unknown tool {name}"}
    if tool["risk"] == "high":
        with tenant_conn(tenant_id) as conn:
            pid = conn.execute(
                "INSERT INTO pending_actions (tenant_id, tool, args) VALUES (%s,%s,%s) RETURNING id",
                (tenant_id, name, json.dumps(args))).fetchone()[0]
        return {"status": "pending_approval", "pending_action_id": pid}
    return {"result": tool["fn"](tenant_id, args)}


def parse_action(text: str) -> dict:
    try:
        return json.loads(text[text.index("{"): text.rindex("}") + 1])
    except Exception:
        return {"final": text.strip(), "citations": []}
