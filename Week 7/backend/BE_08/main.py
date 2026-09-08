from fastapi import FastAPI

app = FastAPI(
    title="PDF Report Generator API",
    version="1.0",
    description="Query SQL data, render HTML-to-PDF via Playwright Chromium, and serve reports by link."
)

@app.get("/health", summary="Health Check", tags=["General"])
def health_check():
    return {"status": "ok"}
