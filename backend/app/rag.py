"""Hybrid retrieval: pgvector cosine + Postgres full-text, fused with Reciprocal Rank Fusion."""
from .db import tenant_conn
from .llm import embed


def chunk_text(text: str, size: int = 900, overlap: int = 150) -> list[str]:
    out, i = [], 0
    while i < len(text):
        out.append(text[i:i + size])
        i += size - overlap
    return out


def ingest(tenant_id: str, source: str, text: str, sensitivity: str = "normal") -> int:
    chunks = chunk_text(text)
    vecs = embed(chunks)
    with tenant_conn(tenant_id) as conn:
        doc_id = conn.execute(
            "INSERT INTO documents (tenant_id, source, sensitivity) VALUES (%s,%s,%s) RETURNING id",
            (tenant_id, source, sensitivity)).fetchone()[0]
        for c, v in zip(chunks, vecs):
            conn.execute(
                "INSERT INTO chunks (tenant_id, document_id, content, embedding) VALUES (%s,%s,%s,%s::vector)",
                (tenant_id, doc_id, c, str(v)))
    return len(chunks)


def retrieve(tenant_id: str, query: str, k: int = 5) -> list[dict]:
    qv = str(embed([query])[0])
    with tenant_conn(tenant_id) as conn:
        vec = conn.execute(
            """SELECT c.id, c.content, d.source, d.sensitivity FROM chunks c
               JOIN documents d ON d.id = c.document_id
               ORDER BY c.embedding <=> %s::vector LIMIT 20""", (qv,)).fetchall()
        fts = conn.execute(
            """SELECT c.id, c.content, d.source, d.sensitivity FROM chunks c
               JOIN documents d ON d.id = c.document_id
               WHERE c.tsv @@ plainto_tsquery('english', %s)
               ORDER BY ts_rank(c.tsv, plainto_tsquery('english', %s)) DESC LIMIT 20""",
            (query, query)).fetchall()
    scores: dict[int, float] = {}
    rows: dict[int, tuple] = {}
    for lst in (vec, fts):
        for rank, row in enumerate(lst):
            scores[row[0]] = scores.get(row[0], 0) + 1 / (60 + rank)   # RRF
            rows[row[0]] = row
    top = sorted(scores, key=scores.get, reverse=True)[:k]
    return [{"id": i, "content": rows[i][1], "source": rows[i][2], "sensitivity": rows[i][3]} for i in top]
    # TODO(v2): add a cross-encoder reranker and measure the hit@5 / groundedness delta in evals/
