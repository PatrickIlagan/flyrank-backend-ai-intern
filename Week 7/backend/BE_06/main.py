import datetime
import uuid
from typing import Dict, Any, Optional

import inngest
import inngest.fast_api
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(
    title="Background Jobs API (Inngest)",
    version="1.0",
    description="A resilient background jobs and durable workflow API using FastAPI and Inngest."
)

# In-memory store for reports (resets on restart)
reports: Dict[str, Dict[str, Any]] = {}

# 1. Initialize Inngest Client (Development Mode)
inngest_client = inngest.Inngest(
    app_id="report-api",
    is_production=False
)

# Pydantic Schemas
class CreateReportRequest(BaseModel):
    topic: str

class ReportResponse(BaseModel):
    id: str
    status: str
    topic: Optional[str] = None
    result: Optional[str] = None


# 2. Inngest Function: say-hello (Stage 1)
@inngest_client.create_function(
    fn_id="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello")
)
async def say_hello(ctx: inngest.Context) -> str:
    # Sleep 5 seconds in the background
    await ctx.step.sleep("sleep-5-seconds", datetime.timedelta(seconds=5))
    return "Hello from the background!"


# 3. Inngest Function: make-report (Stage 2)
@inngest_client.create_function(
    fn_id="make-report",
    trigger=inngest.TriggerEvent(event="report/requested")
)
async def make_report(ctx: inngest.Context) -> dict:
    report_id = ctx.event.data.get("id")
    topic = ctx.event.data.get("topic")

    # Step 1: Simulate the slow work (8 seconds)
    await ctx.step.sleep("do-the-slow-work", datetime.timedelta(seconds=8))

    # Step 2: Build the report and update the store
    def build_report() -> dict:
        result_text = f"Comprehensive executive report on '{topic}', generated after in-depth background analysis."
        if report_id in reports:
            reports[report_id]["status"] = "done"
            reports[report_id]["result"] = result_text
        return {"id": report_id, "status": "done", "result": result_text}

    build_result = await ctx.step.run("build-report", build_report)
    return build_result


# 4. Mount Inngest Endpoint (/api/inngest)
inngest.fast_api.serve(app, inngest_client, [say_hello, make_report])


# 5. REST Endpoints
@app.get("/health", summary="Health Check", tags=["General"])
def health_check():
    return {"status": "ok"}


@app.post(
    "/reports",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Request a new report (Fast Door)",
    tags=["Reports"]
)
async def create_report(payload: CreateReportRequest):
    report_id = str(uuid.uuid4())[:8]
    
    # Store initial pending state
    reports[report_id] = {
        "id": report_id,
        "topic": payload.topic,
        "status": "pending",
        "result": None
    }

    # Dispatch background event to Inngest
    await inngest_client.send(
        inngest.Event(
            name="report/requested",
            data={
                "id": report_id,
                "topic": payload.topic
            }
        )
    )

    # Return immediately with 202 Accepted
    return {
        "id": report_id,
        "status": "pending"
    }


@app.get(
    "/reports/{report_id}",
    summary="Get report status and result",
    tags=["Reports"]
)
def get_report(report_id: str):
    if report_id not in reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return reports[report_id]

