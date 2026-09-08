# PDF Report Generator (FastAPI + SQLite + Playwright)

A production data-to-document report pipeline built in **Python 3.11** with **FastAPI**, **SQLite**, and **Playwright (Chromium)**. The system queries relational data, aggregates metrics via SQL, renders an HTML document with print CSS, prints it to a multi-page PDF via headless Chromium, and serves the generated artifact by link.

Part of **FlyRank AI Backend Engineering Internship: Week 7 (Assignment BE_08 / Assignment A8: PDF report generator)**.

---

## Stages & Checklist

- [x] **Stage 0: The Setup**: Starter FastAPI app with GET /health returning 200, install Playwright, and install Chromium.
- [x] **Stage 1: Data Worth Reporting On**: Seed SQLite database `report.db` with an `orders` table (~200 random rows) and ensure idempotent seeding.
- [ ] **Stage 2: Boring SQL is 80% of Reporting**: Write SQL aggregation queries (totals, averages, top 5, daily breakdown) in `get_report_data()`.
- [ ] **Stage 3: Render: From Numbers to a PDF**: Build HTML report template with print CSS (`page-break-inside: avoid`), render to multi-page PDF via Playwright.
- [ ] **Stage 4: Serve it from your API**: Create `reports` table in SQLite, add `POST /reports` (generates PDF and stores on disk) and `GET /reports/{id}/file` (serves file by link).
- [ ] **Stage 5: Ask Twice, Get One**: Implement idempotency to prevent duplicate report generation on the same day (unless forced).
- [ ] **Stage 6: Publish to GitHub**: Document setup, paste queries, verify clean clone instructions, and publish.

---

## The Core Pipeline

1. **Query:** SQL aggregation turns 200 rows into 4 summary metrics.
2. **Render:** HTML template + metrics are converted to a PDF document via headless Chromium.
3. **Store:** The PDF file is saved to disk (`reports/<id>.pdf`) and its metadata saved to SQLite.
4. **Serve:** Clients retrieve the PDF by link (`GET /reports/{id}/file`) rather than passing megabytes of bytes in JSON.
