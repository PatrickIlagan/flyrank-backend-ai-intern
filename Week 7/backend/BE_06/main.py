"""
FastAPI Server - Week 7 Assignment BE_06 (Your first background job)
Stage 0: Hello, Server
"""

from fastapi import FastAPI

app = FastAPI(
    title="Background Jobs API (Inngest)",
    version="1.0",
    description="A resilient background jobs and durable workflow API using FastAPI and Inngest."
)

@app.get("/health", summary="Health Check", tags=["General"])
def health_check():
    return {"status": "ok"}
