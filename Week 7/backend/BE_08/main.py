import os
import sqlite3
import uuid
import datetime
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from report import get_report_data, generate_html, render_pdf

DB_PATH = "report.db"

app = FastAPI(
    title="PDF Report Generator API",
    version="1.0",
    description="Query SQL data, render HTML-to-PDF via Playwright Chromium, and serve reports by link."
)

def init_db():
    """Ensure the reports bookkeeping table exists next to the orders data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            path TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.get("/health", summary="Health Check", tags=["General"])
def health_check():
    return {"status": "ok"}

@app.post(
    "/reports",
    status_code=status.HTTP_201_CREATED,
    summary="Generate a new PDF report",
    tags=["Reports"]
)
def create_report():
    """
    Executes the full reporting pipeline:
    1. Query: Aggregates SQL data from report.db
    2. Render: Converts metrics to HTML and prints A4 PDF via headless Chromium
    3. Store: Saves file to disk and records metadata in SQLite
    4. Serve: Returns HTTP 201 with the download link
    """
    report_id = str(uuid.uuid4())[:8]
    output_path = f"reports/{report_id}.pdf"

    # Step 1: Query database
    data = get_report_data(DB_PATH)

    # Step 2: Render HTML and convert to PDF via Playwright
    html = generate_html(data)
    render_pdf(html, output_path)

    # Step 3: Store record in database
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reports (id, path, created_at) VALUES (?, ?, ?)",
        (report_id, output_path, created_at)
    )
    conn.commit()
    conn.close()

    # Step 4: Hand out link to the client
    return {
        "id": report_id,
        "file": f"/reports/{report_id}/file"
    }

@app.get(
    "/reports/{report_id}",
    summary="Get report metadata and link",
    tags=["Reports"]
)
def get_report_metadata(report_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, path, created_at FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": row["id"],
        "path": row["path"],
        "created_at": row["created_at"],
        "file": f"/reports/{row['id']}/file"
    }

@app.get(
    "/reports/{report_id}/file",
    summary="Download the generated PDF report",
    tags=["Reports"]
)
def download_report_file(report_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, path FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()

    if not row or not os.path.exists(row["path"]):
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        path=row["path"],
        media_type="application/pdf",
        filename=f"report-{report_id}.pdf"
    )
