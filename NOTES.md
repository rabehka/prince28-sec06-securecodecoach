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
