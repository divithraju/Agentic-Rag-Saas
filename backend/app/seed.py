"""Create demo tenants (run: python -m app.seed)."""
from .db import tenant_conn

for tid, name, policy in [
    ("tenant_a", "Acme Fintech", '{"cost_mode":"balanced","data_residency":"any"}'),
    ("tenant_b", "Campus University", '{"cost_mode":"cheap","data_residency":"on_prem"}'),
]:
    with tenant_conn(tid) as conn:
        conn.execute("INSERT INTO tenants (id,name,policy) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
                     (tid, name, policy))
print("seeded")
