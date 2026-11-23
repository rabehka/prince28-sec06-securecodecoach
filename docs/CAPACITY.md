# Capacity plan: SecureCodeCoach

Full corpus target: Cheat sheets + ASVS 4.0.3 + ASVS 5.0 + WSTG (600+ files)

<!-- generated:start -->
## Measured on my start corpus (2026-11-23 09:25 UTC)

| What | Value |
|---|---|
| Files | 149 |
| Size on disk | 3.0 MB |
| Pages (PDF pages + 1 per 3,000 characters of text/HTML) | 991 |
| Characters of text | 2,972,540 |
| Estimated tokens (characters / 4) | 743,135 |
| Tokens per page | 750 |
| PDFs with almost no text (scanned? OCR is Day 7) | 0 |
| Files not measured (zip, xlsx, unreadable) | 0 |

## Estimate for the full corpus (target: 600 files)

| What | How | Value |
|---|---|---|
| Scale factor | target / measured | x 4.0 |
| Tokens | measured tokens x scale | 2.99 M |
| Raw files | measured MB x scale | 12 MB |
| Chunks | tokens / 400 x 1.15 overlap | 8,603 |
| Embedding cost, one time | tokens x 1.15 x $0.15 per 1M | $0.52 = Rs 49 |
| Vector storage | chunks x 768 numbers x 4 bytes | 26 MB |
| Text in Postgres | characters x scale x 1.2 | 14 MB |

Assumptions: 4 characters per token, 400-token chunks, 768-dimension embeddings at $0.15 per 1M tokens, Rs 95 per US dollar.
<!-- generated:end -->

## What I conclude

1. No, one-time embedding for the full 600-file corpus costs only $0.52 (Rs 49), which is negligible.
2. Yes, 26 MB of vectors plus 14 MB of text (40 MB total) easily fits within Render/Supabase's free 500 MB–1 GB Postgres limit.
3. I am least sure about the estimated 2.99 M tokens (calculated via `characters / 4`), which I will measure accurately using a real tokenizer (`tiktoken`) on Wednesday.
4. At 10x scale (~29.9 M tokens, ~400 MB vectors + text), one-time embedding still costs only ~$5.20 (Rs 490), but storage approaches free-tier Postgres limits (~500 MB) and will require an HNSW/IVFFlat vector index plus a paid database tier.
