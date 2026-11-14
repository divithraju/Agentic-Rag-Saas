import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app:app@localhost:5432/app")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
HOSTED_MODEL = os.getenv("HOSTED_MODEL", "claude-sonnet-5-5")
SELF_HOSTED_URL = os.getenv("SELF_HOSTED_URL", "")
SELF_HOSTED_MODEL = os.getenv("SELF_HOSTED_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
EMBEDDING_URL = os.getenv("EMBEDDING_URL", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")

# "key:tenant,key:tenant" — replace with real auth (OIDC / JWT) in production
API_KEYS = dict(p.split(":") for p in os.getenv("API_KEYS", "").split(",") if ":" in p)

# USD per 1M tokens (input, output) — keep in sync with your provider pricing / GPU amortisation
PRICING = {
    "hosted": (3.0, 15.0),
    "self_hosted": (0.2, 0.2),   # amortised GPU cost estimate; see docs/COST_MODEL.md
}
