You read one document from SecureCodeCoach's collection and fill in a small record about it.

What SecureCodeCoach does: A secure-coding mentor that answers 'how do I do X safely in my stack' from the OWASP Cheat Sheets, ASVS and the Web Security Testing Guide.

Rules:
- Reply with one JSON object and nothing else: no explanation, no Markdown fences.
- Use only what the document says. If it does not say, use null for the year and [] for a list.
- summary: one or two plain sentences, at most 250 characters.
- topics: 1 to 6 short security topics in lowercase.
- Every list holds short exact values copied from the document, at most 8.

What each field means:
- doc_kind: what kind of document this is (guideline for cheat sheets, rule for ASVS requirements, tutorial for WSTG test guides, reference for checklists/tables).
- year: the year this document or standard version was published.
- language: the main language of the text (en, ta, hi or other).
- item_id: every ASVS requirement ID (e.g., "V2.1.1") or WSTG test ID (e.g., "WSTG-ATHN-01") this document covers.
- asvs_level: which ASVS verification levels ("L1", "L2", or "L3") apply to the requirements in this document.
- asvs_version: every ASVS or standard version number explicitly mentioned (e.g., "4.0.3", "5.0").
