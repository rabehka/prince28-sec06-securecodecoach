# Day 10 Ingestion Report

## Run Summary

| Environment | Job ID | Queued | Done | Skipped | Failed | Pages | Duration |
|---|---|---:|---:|---:|---:|---:|---:|
| Local (10 docs) | `a0c122fbb4ab482a92ed7e26f6ca24dc` | 10 | 10 | 0 | 0 | 79 | 132 s |
| Local (20 docs) | `b4c9d14088614ff99aab596cd64e7005` | 20 | 20 | 0 | 0 | 136 | 185 s |
| Local kill test (10 docs) | `0e624a3d67d24db0b37c457cb1ff5555` | 10 | 10 | 0 | 0 | 58 | Recovered (`most_tries=2`) |
| Render live (`securecodecoach.onrender.com`) | `2e2f8c8ad7c74bbcb3f6288c0d4f33ff` | 5 | 5 | 0 | 0 | 43 | 39 s |
| Render live batch 2 (`securecodecoach.onrender.com`) | `0647495ab21e4c828e556234454ab15d` | 5 | 3 | 2 | 0 | 33 | 59 s |

## What I learnt

- Content-hash document IDs (`sha256`) and Postgres state tracking keep worker restarts and retries idempotent without creating duplicate document or record rows.
- Shared token-bucket backpressure (`Pace`) combined with explicit `Retry(defer=...)` vs. `Permanent` error handling prevents provider rate-limit storms and poison-message loops.
- Copying `data/manifest.jsonl` into the runtime Docker image and configuring Upstash TLS (`rediss://`) enabled the Render in-process worker to ingest live documents with zero failures.
