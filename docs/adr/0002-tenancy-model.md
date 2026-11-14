# ADR-0002: Tenancy via shared schema + Postgres Row-Level Security

**Status:** Accepted

## Decision
Single schema, `tenant_id` on every row, RLS policies keyed on `app.tenant_id` set per connection.

## Why
Lower ops overhead than schema-per-tenant; isolation enforced by the database, so an app bug cannot leak across tenants.

## Trade-offs
Noisy-neighbour risk (mitigate with per-tenant limits); very large tenants may later move to dedicated DBs.
