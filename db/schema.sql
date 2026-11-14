CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE tenants (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  policy JSONB NOT NULL DEFAULT '{"cost_mode":"balanced","data_residency":"any"}'
);

CREATE TABLE documents (
  id BIGSERIAL PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id),
  source TEXT NOT NULL,
  sensitivity TEXT NOT NULL DEFAULT 'normal',   -- normal | restricted
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE chunks (
  id BIGSERIAL PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id),
  document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
  embedding vector(1024)
);
CREATE INDEX chunks_tsv_idx ON chunks USING GIN (tsv);
CREATE INDEX chunks_vec_idx ON chunks USING hnsw (embedding vector_cosine_ops);

CREATE TABLE llm_calls (
  id BIGSERIAL PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  ts TIMESTAMPTZ DEFAULT now(),
  route TEXT NOT NULL,            -- hosted | self_hosted
  model TEXT NOT NULL,
  reason TEXT,
  prompt_tokens INT, completion_tokens INT,
  latency_ms INT,
  cost_usd NUMERIC(12,6)
);

CREATE TABLE pending_actions (
  id BIGSERIAL PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  tool TEXT NOT NULL,
  args JSONB NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',   -- pending | approved | rejected
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Row-Level Security: every query must run with SET app.tenant_id = '<tenant>'
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE pending_actions ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON documents USING (tenant_id = current_setting('app.tenant_id', true));
CREATE POLICY tenant_isolation ON chunks USING (tenant_id = current_setting('app.tenant_id', true));
CREATE POLICY tenant_isolation ON pending_actions USING (tenant_id = current_setting('app.tenant_id', true));
-- NOTE: connect as a non-superuser, non-owner role in production so RLS is enforced
-- (table owners bypass RLS unless FORCE ROW LEVEL SECURITY is set).
ALTER TABLE documents FORCE ROW LEVEL SECURITY;
ALTER TABLE chunks FORCE ROW LEVEL SECURITY;
ALTER TABLE pending_actions FORCE ROW LEVEL SECURITY;
