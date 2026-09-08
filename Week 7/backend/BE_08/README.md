# PDF Report Generator (FastAPI + SQLite + Playwright)

A production data-to-document report pipeline built in **Python 3.11** with **FastAPI**, **SQLite**, and **Playwright (Chromium)**. The system queries relational data, aggregates metrics via SQL, renders an HTML document with print CSS, prints it to a multi-page PDF via headless Chromium, and serves the generated artifact by link.

Part of **FlyRank AI Backend Engineering Internship: Week 7 (Assignment BE_08 / Assignment A8: PDF report generator)**.

---

## Stages & Checklist

- [x] **Stage 0: The Setup**: Starter FastAPI app with GET /health returning 200, install Playwright, and install Chromium.
- [x] **Stage 1: Data Worth Reporting On**: Seed SQLite database `report.db` with an `orders` table (200 rows) with idempotent reseeding.
- [x] **Stage 2: Boring SQL is 80% of Reporting**: Write SQL aggregation queries (totals, averages, top 5 products, 7-day trend, full orders list) in `get_report_data()`.
- [x] **Stage 3: Render: From Numbers to a PDF**: Build HTML report template with print CSS (`page-break-inside: avoid`, repeating `thead`), render to multi-page PDF via headless Chromium.
- [x] **Stage 4: Serve it from your API**: Create `reports` table in SQLite, implement `POST /reports` (generates PDF and stores on disk), `GET /reports/{id}` (metadata), and `GET /reports/{id}/file` (serves file by link).
- [x] **Stage 5: Ask Twice, Get One**: Implement daily idempotency to prevent duplicate report generation on the same day (unless forced with `?force=true`).
- [x] **Stage 6: Publish to GitHub**: Document setup, paste queries, verify clean clone instructions, and publish.

---

## The Core Pipeline

1. **Query:** SQL aggregation transforms 200 raw database rows into 4 summary metrics.
2. **Render:** HTML template + metrics are converted to an A4 multi-page PDF document via headless Chromium.
3. **Store:** The PDF file is saved to disk (`reports/<id>.pdf`) and its metadata recorded in SQLite.
4. **Serve:** Clients retrieve the PDF by link (`GET /reports/{id}/file`) rather than passing megabytes of raw bytes in JSON.
5. **Cache:** Duplicate requests for the same day return the existing report link in under 30 ms without spinning up Chromium.

---

## Architecture Overview

```
Client Request
      │
      ├── POST /reports (No body or ?force=true)
      │         │
      │         ├── Check SQLite reports table for today's report
      │         │     ├── Found & not forced: Return existing link (HTTP 200, ~20ms)
      │         │     └── Missing or forced: Proceed with generation (HTTP 201, ~1.5s)
      │         │
      │         ├── Step 1: Query SQLite (report.db)
      │         │     └── 4 SQL aggregations (Totals, Top 5, 7-Day Trend, Orders List)
      │         │
      │         ├── Step 2: Render HTML + Print CSS
      │         │     └── Injects metrics into HTML with page-break-inside & repeating headers
      │         │
      │         ├── Step 3: Headless Chromium (Playwright)
      │         │     └── Renders A4 PDF with exact margins and background colors
      │         │
      │         ├── Step 4: Disk & SQLite Storage
      │         │     ├── Save reports/<id>.pdf to disk
      │         │     └── INSERT INTO reports (id, path, created_at)
      │         │
      │         └── Return JSON: {"id": "...", "file": "/reports/<id>/file"}
      │
      └── GET /reports/{id}/file
                │
                └── Streams binary PDF via FileResponse (application/pdf)
```

---

## Database Schema & Seeding

The database uses SQLite (`report.db`) with two tables:

### 1. `orders` Table
Stores raw transaction data:
```sql
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer TEXT NOT NULL,
    product TEXT NOT NULL,
    amount REAL NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

Seeded via `seed.py` with 200 realistic orders spread over the past 30 days across 8 products (`Laptop`, `Smartphone`, `Headphones`, `Monitor`, `Keyboard`, `Mouse`, `Tablet`, `Smartwatch`) and 4 order statuses (`completed`, `shipped`, `pending`, `cancelled`).

**Idempotent Seeding:** `seed.py` runs `DELETE FROM orders` before inserting, ensuring repeated executions always result in exactly 200 rows.

### 2. `reports` Table
Stores metadata for generated reports:
```sql
CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY,
    path TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

---

## SQL Aggregation Queries

All aggregation logic is implemented in `get_report_data()` in `report.py`:

### 1. High-Level Totals (COUNT, SUM, AVG)
```sql
SELECT 
    COUNT(*) AS total_orders,
    ROUND(SUM(amount), 2) AS total_revenue,
    ROUND(AVG(amount), 2) AS avg_order_value
FROM orders;
```

### 2. Top 5 Products by Revenue
```sql
SELECT 
    product,
    COUNT(*) AS order_count,
    ROUND(SUM(amount), 2) AS total_revenue
FROM orders
GROUP BY product
ORDER BY total_revenue DESC
LIMIT 5;
```

### 3. Last 7 Days Daily Revenue Trend
```sql
SELECT 
    strftime('%Y-%m-%d', created_at) AS order_date,
    COUNT(*) AS order_count,
    ROUND(SUM(amount), 2) AS daily_revenue
FROM orders
WHERE created_at >= date('now', '-7 days')
GROUP BY strftime('%Y-%m-%d', created_at)
ORDER BY order_date ASC;
```

### 4. Full Orders List (for Appendix Table)
```sql
SELECT 
    id,
    customer,
    product,
    ROUND(amount, 2) AS amount,
    status,
    created_at
FROM orders
ORDER BY created_at DESC;
```

---

## HTML & CSS Print Layout Rules

Rendering clean multi-page PDFs requires specific CSS Print Media techniques:

1. **Page Margins & Sizing (`@page`):**
   ```css
   @page {
       size: A4;
       margin: 15mm;
   }
   ```
   Ensures standard A4 page dimensions across all PDF viewers and printers.

2. **Preventing Broken Table Rows (`page-break-inside: avoid`):**
   ```css
   tr {
       page-break-inside: avoid;
   }
   .card {
       page-break-inside: avoid;
   }
   ```
   Without this rule, Chromium might slice a table row or card directly in half across two pages. With `avoid`, Chromium neatly moves the entire row to the next page if it doesn't fit.

3. **Repeating Table Headers (`display: table-header-group`):**
   ```css
   thead {
       display: table-header-group;
   }
   ```
   For a 14-page detailed orders table, readers need column titles on every page. This rule forces Chromium to reprint the header row at the top of every new page.

4. **Background Color Preservation:**
   Playwright's `print_background=True` parameter ensures CSS backgrounds, colored status badges, and table header colors are retained in the PDF output.

---

## API Endpoints

### 1. `GET /health`
- **Purpose:** Health check endpoint.
- **Response:** `200 OK`
  ```json
  {"status": "ok"}
  ```

### 2. `POST /reports`
- **Purpose:** Initiates report generation with daily idempotency.
- **Query Parameters:**
  - `force` (bool, optional, default: `false`): Set `true` to force fresh PDF generation even if one already exists for today.
- **Request Body (optional):**
  ```json
  {"force": true}
  ```
- **Responses:**
  - Fresh generation: `201 Created`
    ```json
    {
      "id": "e88c32b4",
      "file": "/reports/e88c32b4/file",
      "cached": false
    }
    ```
  - Idempotent hit: `200 OK`
    ```json
    {
      "id": "e88c32b4",
      "file": "/reports/e88c32b4/file",
      "cached": true
    }
    ```

### 3. `GET /reports/{report_id}`
- **Purpose:** Fetch metadata for a previously generated report.
- **Response:** `200 OK`
  ```json
  {
    "id": "e88c32b4",
    "path": "reports/e88c32b4.pdf",
    "created_at": "2026-09-08 17:35:20",
    "file": "/reports/e88c32b4/file"
  }
  ```

### 4. `GET /reports/{report_id}/file`
- **Purpose:** Download or stream the generated PDF file.
- **Response:** Binary stream with `Content-Type: application/pdf` and `Content-Disposition: attachment; filename="report-<id>.pdf"`.

---

## Verification & Timing Proof

### Idempotency Timing Comparison

```bash
# 1. First run: Chromium launches, generates HTML, renders PDF (~1.5s)
$ time curl -i -X POST http://localhost:8000/reports
HTTP/1.1 201 Created
{"id":"e88c32b4","file":"/reports/e88c32b4/file","cached":false}
real    0m1.482s

# 2. Second run: Instant cache hit, no Chromium launch (~20ms)
$ time curl -i -X POST http://localhost:8000/reports
HTTP/1.1 200 OK
{"id":"e88c32b4","file":"/reports/e88c32b4/file","cached":true}
real    0m0.022s

# 3. Force bypass: Fresh report created (~1.4s)
$ time curl -i -X POST "http://localhost:8000/reports?force=true"
HTTP/1.1 201 Created
{"id":"67145af9","file":"/reports/67145af9/file","cached":false}
real    0m1.411s
```

### PDF Download Verification

```bash
$ curl -o sales-report.pdf http://localhost:8000/reports/e88c32b4/file
$ ls -lh sales-report.pdf
-rw-r--r-- 1 user group 150K sales-report.pdf
```

---

## Setup & Running Locally

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Setup Virtual Environment
```bash
python -m venv venv

# Windows (Git Bash):
source venv/Scripts/activate

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies & Headless Chromium
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Seed the Database
```bash
python seed.py
```
Outputs confirmation of 200 orders seeded into `report.db`.

### 5. Start the FastAPI Server
```bash
uvicorn main:app --reload --port 8000
```
The API is live at `http://localhost:8000` with interactive Swagger docs at `http://localhost:8000/docs`.

---

## Personal Experience & Key Takeaways

### My Experience
This is probably one of the most useful assignments ever as generating reports are probably one of the most efficient things ever. I got to learn about chromium headless and its pdf rendering using CSS and HTML which was something a bit more different. It's not the first time I've encountered or used this before but it was definitely an assignment where it made me realize how important it could actually be to those in different departments for companies.

### Key Takeaways
- **Boring SQL is 80% of Reporting:** Efficient backend reporting starts with doing the heavy lifting in SQLite/PostgreSQL with `SUM`, `AVG`, `GROUP BY`, and `strftime`, rather than pulling thousands of raw rows into Python memory.
- **Chromium Print Engine Over Antiquated Tools:** Headless Chromium through Playwright replaces cumbersome libraries like ReportLab or outdated tools like wkhtmltopdf. HTML and modern CSS flexbox provide an intuitive and beautiful design surface.
- **CSS Print Media Rules are Critical:** For clean multi-page documents, `page-break-inside: avoid` on cards/rows and `thead { display: table-header-group; }` on tables are essential to avoid awkward page breaks and unreadable headers.
- **Link-Based Distribution Pattern:** Never pass megabytes of binary or base64 data inside JSON responses. Generating files to disk and handing out streamable links (`FileResponse`) is scalable and memory-efficient.
- **Idempotency Protects Server Resources:** Expensive operations like PDF rendering must be shielded by daily idempotency checks, preventing duplicate renders while providing an explicit `force=true` bypass for real updates.
