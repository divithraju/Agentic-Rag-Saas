"""Model router: choose hosted vs self-hosted per request. See docs/adr/0001-hybrid-inference-routing.md"""
from dataclasses import dataclass
from .config import HOSTED_MODEL, SELF_HOSTED_MODEL, SELF_HOSTED_URL


@dataclass
class Route:
    backend: str   # hosted | self_hosted
    model: str
    reason: str


def choose_route(policy: dict, sensitivity: str, prompt_tokens: int, task: str = "answer") -> Route:
    self_ok = bool(SELF_HOSTED_URL)
    # 1. Data policy beats everything: restricted data / on-prem residency never leaves the network.
    if sensitivity == "restricted" or policy.get("data_residency") == "on_prem":
        if not self_ok:
            raise RuntimeError("Restricted data but no self-hosted model configured")
        return Route("self_hosted", SELF_HOSTED_MODEL, "data policy")
    # 2. Cheap tier: short, low-stakes tasks go to the self-hosted model.
    if self_ok and policy.get("cost_mode") == "cheap" and prompt_tokens < 1500 and task in {"classify", "summarize"}:
        return Route("self_hosted", SELF_HOSTED_MODEL, "cost tier")
    # 3. Default: best quality.
    return Route("hosted", HOSTED_MODEL, "default quality")
