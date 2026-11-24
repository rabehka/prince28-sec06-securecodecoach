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
