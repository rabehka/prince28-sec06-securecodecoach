# Engineering notes: SecureCodeCoach

## D03 · PostgreSQL

### Migrations (upgrade, downgrade, upgrade)

```text
INFO  [alembic.runtime.migration] Running downgrade c23c65eaec90 -> 37f196e109b0, add GIN index to document metadata
37f196e109b0
INFO  [alembic.runtime.migration] Running upgrade 37f196e109b0 -> c23c65eaec90, add GIN index to document metadata
37f196e109b0 -> c23c65eaec90 (head), add GIN index to document metadata
<base> -> 37f196e109b0, create documents and pages
```markdown
## D05

- **Lead time:** ~3 minutes from merging PR to `main` until `/health` returns the new commit SHA on Render.
- **Rollback drill:** Verified rolling back to a previous working commit/image via Render dashboard and confirming `/health` status.
## D06 · Collecting the corpus

- Start target: Cheat sheets (about 100 files)
- Collected today: 149 files, 991 pages, 3.0 MB (from DATASET.md)
- Doors used: URL list / Git repository

### Licence check

| Source | Licence or terms, in my words | May I show full text in answers? |
|---|---|---|
| OWASP CheatSheetSeries (`raw.githubusercontent.com` & Git repo) | CC BY-SA 4.0: free to download, store, and adapt with attribution and share-alike for derived text. | Yes, with attribution link to the original OWASP cheat sheet and CC BY-SA 4.0 credit. |

### robots.txt

- Site: `https://raw.githubusercontent.com/robots.txt` . Its robots.txt says (2 lines): `User-agent: *` with `Disallow: /` for most paths, while GitHub's `github.com/robots.txt` allows public repository cloning/browsing with crawl delays.
- Was anything blocked for my bot? What did I do about it? Door 1 (`raw.githubusercontent.com`) allowed the 10 direct Markdown fetches (`blocked=0`), and I used Door 2 (`git clone` of `OWASP/CheatSheetSeries`) to fetch all 139 cheat sheets cleanly without hammering HTTP endpoints.

### Kill and resume

- Run 1: I pressed Ctrl+C after 7 files
- Run 2: downloaded=3 skipped=7
- Run 3: downloaded=0 skipped=10

### Capacity (from docs/CAPACITY.md)

- Tokens per page, measured: 750
- Full corpus: 2.99 M tokens, 8,603 chunks, embedding about Rs 49, vectors 26 MB
- The number that surprised me most, and why (2 lines): Embedding the entire 600-file security corpus costs only Rs 49 ($0.52) and takes just 40 MB in Postgres. I expected security documentation to require hundreds of megabytes and much higher API spend.

### One thing that went wrong today, and how I fixed it

- Running Door 2 (`scripts/fetch.py repo`) with `--source owasp-cheatsheets` failed because `data\raw\owasp-cheatsheets` already contained the 10 files from Door 1. I fixed it by passing `--source owasp-cheatsheets-repo` so `git clone` wrote into a clean target directory.

### Crawl in numbers (stretch)

- Files and megabytes per source: `owasp-cheatsheets` = 10 files (0.34 MB); `owasp-cheatsheets-repo` = 139 files (2.67 MB); Total = 149 files (3.01 MB).
- Slowest site: `raw.githubusercontent.com` (HTTP Door 1 took ~7.0s for 10 files due to 0.5s polite per-host crawl delay, compared to ~1.5s for the Git repo clone of 139 files).
- Retries needed: 0 files required more than one attempt (`RETRIES: 0`, 0 failed, 0 blocked).
