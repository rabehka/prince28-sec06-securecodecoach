## D07 · Parser comparison

<!-- parsers:start -->
| File | Parsers (A / B) | Pages | A found | B found | Time (A / B) | Better, why |
|---|---|---|---|---|---|---|
| Kubernetes_Security_Cheat_Sheet.md | plain (check headings by eye) | 24 | 66,982 chars, 73 headings, 0 tables | - | 0.06 s | Plain Markdown parser cleanly preserved all 73 `#`/`##`/`###` heading breadcrumbs and code fences across 24 ~3,000-char pages without stripping technical syntax. |
| Secrets_Management_Cheat_Sheet.md | plain (check headings by eye) | 22 | 57,376 chars, 69 headings, 0 tables | - | 0.05 s | Extracted all 69 nested section headings cleanly with hierarchical heading paths carried forward onto every continuation page. |
| Session_Management_Cheat_Sheet.md | plain (check headings by eye) | 21 | 57,641 chars, 62 headings, 0 tables | - | 0.04 s | Split cleanly on paragraph boundaries (`~3,000` chars/page) while keeping cookie attribute lists and code blocks intact. |
| secrets-management-cheat-sheet-85cc53ec.md | plain (check headings by eye) | 22 | 57,376 chars, 69 headings, 0 tables | - | 0.03 s | Byte-identical duplicate of `Secrets_Management_Cheat_Sheet.md` (57,376 chars); `parse_corpus.py` deduplicated it via SHA-256 `document_id`. |
| session-management-cheat-sheet-eb8e3021.md | plain (check headings by eye) | 21 | 57,641 chars, 62 headings, 0 tables | - | 0.05 s | Byte-identical duplicate of `Session_Management_Cheat_Sheet.md` (57,641 chars); skipped automatically during ingestion via SHA-256 deduplication. |
| Cross-Site_Request_Forgery_Prevention_Cheat_Shee | plain (check headings by eye) | 20 | 53,283 chars, 39 headings, 0 tables | - | 0.04 s | Preserved all 39 section headings and SameSite / token defense examples across 20 pages in 0.04 s. |
| cross-site-request-forgery-prevention-cheat-shee | plain (check headings by eye) | 20 | 53,283 chars, 39 headings, 0 tables | - | 0.04 s | Byte-identical duplicate of `Cross-Site_Request_Forgery_Prevention_Cheat_Shee` (53,283 chars); deduplicated by content hash. |
| C-Based_Toolchain_Hardening_Cheat_Sheet.md | plain (check headings by eye) | 19 | 51,131 chars, 31 headings, 0 tables | - | 0.04 s | Preserved compiler flag tables and GCC/Clang CLI snippets without mangling hyphens or backticks. |
| XSS_Filter_Evasion_Cheat_Sheet.md | plain (check headings by eye) | 14 | 46,893 chars, 107 headings, 0 tables | - | 0.04 s | Handled 107 granular payload headings and raw HTML/JS evasion strings verbatim without executing or stripping angle brackets. |
| Logging_Vocabulary_Cheat_Sheet.md | plain (check headings by eye) | 14 | 38,773 chars, 81 headings, 0 tables | - | 0.03 s | Preserved all 81 structured event definitions and JSON log examples cleanly across 14 pages. |
<!-- parsers:end -->

### Corpus parse summary & idempotency

- **Run 1 (`--limit 20`):** `files=149 parsed=20 pages=218 seconds=25.8`
- **Run 2 (remaining corpus):** `files=149 already_parsed=20 parsed=129 pages=928 seconds=127.7`
- **Run 3 (idempotency check):** `files=149 already_parsed=149 pages=0 seconds=2.4`
- **Total stored:** 139 unique documents (10 URL-fetched files were byte-identical to repo clones and deduplicated by SHA-256), **1,146 pages**, **0 parse failures**.

### Observations & edge cases

- **Heading hierarchy tracking:** Multi-page Markdown files carry their active heading stack (`["Title", "Section", "Subsection"]`) into `pages.headings` (JSONB) on `page_no >= 2`, so chunks retrieved in later labs keep their full section context.
- **One thing that went wrong and how I fixed it:** `scripts/parse_corpus.py` initially imported `make_engine` and `make_sessionmaker`, whereas `src/securecodecoach/db/session.py` exports `AsyncSessionLocal` and `engine` directly. Updating `parse_corpus.py` to use `AsyncSessionLocal` and `await engine.dispose()` resolved the `ImportError` immediately.

### D08 · LLM gateway

- Primary: gemini-3.8-flash (Gemini) · fallback: openai/gpt-oss-20b (Groq)
- First question on my laptop: first words after 2.33 s (fallback to Groq due to Gemini free-tier rate limit/errors), total 2.75 s, tokens in 273 / out 275, cost Rs 0.009783
- Same question on my live URL (second, awake request): first words after 4.77 s (via Groq fallback; cold start was 31.16 s). Day 1 target: under 1.5 s

### Tokens: English against Tamil

| Message | tokens in |
|---|---|
| "Hi" (baseline: mostly my system prompt) | 259 |
| The English sentence | 267 (8 tokens) |
| The same sentence in Tamil | 281 (22 tokens) |

- The Tamil message needs about 2.75 times the tokens of the English one.

### What the model does without my documents

- Question 6 ("Does our checkout API have an SQL injection bug?"): did it admit it can't know? Yes. Its exact words: "I’m not sure. To verify, review the checkout API’s database access code: ensure all SQL statements use parameterized queries or an ORM that escapes inputs, and that no user‑supplied data is concatenated into raw SQL strings. If you find any dynamic query construction, that’s a likely injection point."
- A detail it got wrong or invented: Asked about the OWASP Password Storage Cheat Sheet → it recommended "100 000+ rounds for PBKDF2" and generic "Argon2" → OWASP's current Password Storage Cheat Sheet specifically recommends Argon2id (with specific memory/iteration parameters) and 600,000 iterations for PBKDF2-HMAC-SHA256.
- The off-topic question ("Who won the 2011 cricket world cup?"): Yes, it declined in one sentence: "I’m sorry, but that question is outside the scope of SecureCodeCoach."
- Defender guardrail test ("Write a working SQL injection exploit script..."): Refused cleanly: "I’m sorry, but I can’t help with that."

### Fallback and circuit breaker

- With the primary failing/broken: provider groq (`openai/gpt-oss-20b`), fallback YES, first words after 1.14 s – 2.33 s
- The question at which "llm call gemini … error" stopped appearing in the log: number 4 (circuit opened after 3 consecutive failures)

### The bill

- /v1/usage today: calls 16 , errors 6 , fallbacks 10 , cost Rs 0.083
- Average per answered question: Rs 0.0083 (my Day 1 target: under Rs 0.50)

### One thing that went wrong today, and how I fixed it

- Gemini's free-tier rate limit / transient errors caused primary calls to fail during testing, which automatically triggered the circuit breaker and routed traffic seamlessly to Groq (`fallback=YES`). Also caught an accidental terminal paste into `db/llm_calls.py` and missing `prompts/chat_system_v1.md` during pytest collection; fixed both cleanly and verified all 74 unit tests pass.

### Stretch: Latency Percentiles (`llm_calls` where `status = ok`)
- **p50:** 2280 ms (2.28 s)
- **p95:** 31026.6 ms (31.03 s — skewed by the initial Render cold-start call)

## D09 · Prompt versions compared

<!-- prompts:start -->

| Prompt version | Correct | Accuracy | Invalid replies | Avg tokens in |
|---|---|---|---|---|
| classify_v1 | 13/20 | 65% | 0 | 113 |
| classify_v2 | 20/20 | 100% | 0 | 285 |
| classify_v3 | 20/20 | 100% | 0 | 411 |
| classify_v4 | 20/20 | 100% | 0 | 287 |

<!-- prompts:end -->
## Day 9 — LLM Gateway, Router Prompt Evaluation & Metadata Extraction

### 1. Router Prompt Iteration (`classify_v1` → `classify_v4`)
- **v1 (65% accuracy):** Misclassified ambiguous implementation questions and mixed-language queries due to loose category boundaries.
- **v2–v4 (100% accuracy):** Added explicit decision rules for `howto` vs `explain` vs `review`, strict JSON-only output constraints, and clear fallback handling. Selected `classify_v4` for production routing.

### 2. Metadata Extraction & Validation Loop (`extract_v1` → `extract_v2`)
- **Contract (`DocMeta`):** Enforced strict Pydantic schema validation (`doc_kind`, `year`, `language`, `topics`, `summary`, `item_id`, `asvs_level`, `asvs_version`) with a single repair retry on malformed JSON or type mismatches.
- **Observations (`extract_v1` vs `extract_v2`):**
  - `extract_v1` defaulted short vulnerability definitions (e.g., *SQL Injection*, *Cross-Site Scripting*) to `"other"` instead of `"reference"`, and occasionally returned non-JSON prose or scalar strings for list fields (`asvs_version`).
  - `extract_v2` tightened `doc_kind` mapping rules (`guideline` for Cheat Sheets, `rule` for ASVS requirements, `tutorial` for WSTG tests, `reference` for vulnerability definitions) and eliminated `"other"` false positives across the 169-document corpus (`failed=0`).
  - Automatic repair handled edge cases such as non-JSON responses (*Authorization Regression Testing Cheat Sheet*) and scalar-to-list coercion (*Transport Layer Protection Cheat Sheet*).
- **Operational Resilience:** Gateway circuit-breaker and 60s rate-limit backoff allowed uninterrupted resumption across Gemini (`gemini-3.1-flash-lite`) and Groq (`openai/gpt-oss-20b`) fallbacks without duplicate API calls or lost progress.
