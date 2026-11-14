from contextlib import contextmanager
from psycopg_pool import ConnectionPool
from .config import DATABASE_URL

pool = ConnectionPool(DATABASE_URL, min_size=1, max_size=10, open=False)


@contextmanager
def tenant_conn(tenant_id: str):
    """Connection scoped to one tenant — Postgres RLS enforces isolation."""
    if pool.closed:
        pool.open()
    with pool.connection() as conn:
        conn.execute("SELECT set_config('app.tenant_id', %s, false)", (tenant_id,))
        try:
            yield conn
        finally:
            conn.execute("RESET app.tenant_id")
