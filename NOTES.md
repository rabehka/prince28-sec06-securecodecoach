# Engineering notes: SecureCodeCoach

## D03 · PostgreSQL

### Migrations (upgrade, downgrade, upgrade)

```text
INFO  [alembic.runtime.migration] Running downgrade c23c65eaec90 -> 37f196e109b0, add GIN index to document metadata
37f196e109b0
INFO  [alembic.runtime.migration] Running upgrade 37f196e109b0 -> c23c65eaec90, add GIN index to document metadata
37f196e109b0 -> c23c65eaec90 (head), add GIN index to document metadata
<base> -> 37f196e109b0, create documents and pages
```

### The loader is idempotent

```text
run 1: Inserted: 20  Unchanged: 0  Updated: 0
run 2: Inserted: 0  Unchanged: 20  Updated: 0
run 3 (after editing one record): Inserted: 0  Unchanged: 19  Updated: 1
```

### EXPLAIN for ?severity=High

```text
-- 1) What the planner chooses on its own:
Seq Scan on documents  (cost=0.00..1.25 rows=1 width=36) (actual time=0.013..0.019 rows=13.00 loops=1)
  Filter: (metadata @> '{"severity": "High"}'::jsonb)
  Rows Removed by Filter: 7
  Buffers: shared hit=1
Planning Time: 3.887 ms
Execution Time: 0.046 ms

-- 2) Seq scan switched off, to prove the index can be used:
Bitmap Heap Scan on documents  (cost=12.93..16.94 rows=1 width=36) (actual time=0.067..0.072 rows=13.00 loops=1)
  Recheck Cond: (metadata @> '{"severity": "High"}'::jsonb)
  Heap Blocks: exact=1
  ->  Bitmap Index Scan on ix_documents_metadata_gin  (cost=0.00..12.93 rows=1 width=0) (actual time=0.047..0.047 rows=13.00 loops=1)
        Index Cond: (metadata @> '{"severity": "High"}'::jsonb)
Planning Time: 0.079 ms
Execution Time: 0.168 ms
```

Why did the planner choose a Seq Scan on my table?
The table has only 20 rows, all in one 8 KB page. Reading that one page (cost 1.25) is cheaper than using the index (cost 16.94), and 13 of the 20 rows match anyway.

When would it switch to the GIN index?
When the table grows to thousands of rows and the filter matches only a small fraction of them.

## D04 · Docker, Compose & Testing

### Container Build & Security

- Multi-stage `Dockerfile` (`ghcr.io/astral-sh/uv:python3.12-bookworm-slim` builder -> `python:3.12-slim-bookworm` runtime).
- Final image size: **308 MB** (under 400 MB target).
- Runs as non-root user `appuser` (`uid=1001`) with a built-in `/health` `HEALTHCHECK`.

### Docker Compose Stack

- Services: `db` (`postgres:16-alpine`), `redis` (`redis:7-alpine`), and `api` (`service_healthy` dependency gating).
- On startup, `api` runs `alembic upgrade head` and `python scripts/load_db.py` before serving Uvicorn.

### Test Suite Split & Coverage

- `tests/unit/` — 19 fast unit tests using in-memory repository fakes.
- `tests/integration/` — 3 PostgreSQL integration tests running against an isolated `securecodecoach_test` database created and dropped automatically per test.
- Total: **22 passed in 3.55s**, **95% statement coverage** across `src/securecodecoach`.

### Real Evidence Outputs
```text
IMAGE                 ID             DISK USAGE   CONTENT SIZE   EXTRA
securecodecoach:dev   ab4bccafc7ef        308MB           72MB   U
uid=1001(appuser) gid=1001(appgroup) groups=1001(appgroup)
NAME                        IMAGE                 COMMAND                  SERVICE   CREATED          STATUS                      PORTS
securecodecoach-api-1       securecodecoach:dev   "uvicorn 'securecodeâ€¦"   api       24 minutes ago   Exited (3) 23 minutes ago
securecodecoach-db-1        postgres:16-alpine    "docker-entrypoint.sâ€¦"   db        24 minutes ago   Up 24 minutes (healthy)     0.0.0.0:5433->5432/tcp, [::]:5433->5432/tcp
securecodecoach-migrate-1   securecodecoach:dev   "sh -c 'alembic upgrâ€¦"   migrate   24 minutes ago   Exited (0) 23 minutes ago
securecodecoach-redis-1     redis:7-alpine        "docker-entrypoint.sâ€¦"   redis     24 minutes ago   Up 24 minutes (healthy)     0.0.0.0:6379->6379/tcp, [::]:6379->6379/tcp
migrate-1  | Updated: 0
19 passed, 7 skipped in 2.53s
```
