import uuid
import datetime
import asyncio
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import inngest
import inngest.fast_api

from inngest_client import inngest_client
from workflow import execute_workflow, run_workflow_direct, runs, DEFAULT_WORKFLOW

app = FastAPI(
    title="Visual AI Workflow API",
    version="1.0",
    description="Backend API orchestrating visual AI decision workflows via Inngest and OpenAI."
)

# Enable CORS for frontend visualizer
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExecuteWorkflowRequest(BaseModel):
    context: str
    nodes: Optional[List[Dict[str, Any]]] = None
    edges: Optional[List[Dict[str, Any]]] = None
    start_node_id: Optional[str] = None

@app.get("/", summary="Root Endpoint", tags=["General"])
def root():
    return {
        "message": "Visual AI Workflow API is running",
        "app": "visual-ai-workflow",
        "health": "/health",
        "docs": "/docs",
        "inngest": "/api/inngest"
    }

@app.get("/health", summary="Health Check", tags=["General"])
def health_check():
    return {
        "status": "ok",
        "app": "visual-ai-workflow",
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/api/workflow/template", summary="Get Starter Workflow Template", tags=["Workflow"])
def get_template():
    return DEFAULT_WORKFLOW

@app.post(
    "/api/workflow/execute",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger Workflow Execution via Inngest",
    tags=["Workflow"]
)
async def trigger_workflow(payload: ExecuteWorkflowRequest):
    if not payload.context.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User context is required and cannot be empty"
        )

    run_id = str(uuid.uuid4())[:8]
    active_nodes = payload.nodes if payload.nodes else DEFAULT_WORKFLOW["nodes"]
    active_edges = payload.edges if payload.edges else DEFAULT_WORKFLOW["edges"]
    start_id = payload.start_node_id or (active_nodes[0]["id"] if active_nodes else "node-1")

    # Initialize run record
    runs[run_id] = {
        "id": run_id,
        "status": "running",
        "context": payload.context.strip(),
        "active_node_id": start_id,
        "active_edge_id": None,
        "steps": [],
        "created_at": datetime.datetime.now().isoformat(),
        "completed_at": None
    }

    # Dispatch event to Inngest with fallback to direct async execution
    try:
        await inngest_client.send(
            inngest.Event(
                name="workflow/execute",
                data={
                    "run_id": run_id,
                    "context": payload.context.strip(),
                    "nodes": active_nodes,
                    "edges": active_edges,
                    "start_node_id": start_id
                }
            )
        )
    except Exception as e:
        # Fallback to direct background execution if Inngest dev server is unreachable
        asyncio.create_task(
            run_workflow_direct(
                run_id=run_id,
                context=payload.context.strip(),
                nodes=active_nodes,
                edges=active_edges,
                start_node_id=start_id
            )
        )

    return {
        "run_id": run_id,
        "status": "running",
        "poll_url": f"/api/workflow/runs/{run_id}"
    }

@app.get("/api/workflow/runs/{run_id}", summary="Get Workflow Run Status", tags=["Workflow"])
def get_run_status(run_id: str):
    if run_id not in runs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run {run_id} not found"
        )
    return runs[run_id]

# Mount Inngest Endpoint (/api/inngest)
inngest.fast_api.serve(app, inngest_client, [execute_workflow])
