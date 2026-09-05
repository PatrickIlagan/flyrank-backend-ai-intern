import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.llm.schema import TriageRequest, TriageResponse, CategoryEnum, UrgencyEnum

load_dotenv()

app = FastAPI(
    title="Production LLM Triage API",
    version="1.0",
    description="A resilient customer support message triage API backed by an LLM."
)

# Custom 400 Bad Request handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    field = errors[0]["loc"][-1] if errors and "loc" in errors[0] else "body"
    msg = errors[0]["msg"] if errors else "Invalid input"
    return JSONResponse(
        status_code=400,
        content={"error": f"Validation failed on field '{field}': {msg}"}
    )

@app.get("/", summary="API Root", tags=["General"])
def read_root():
    return {
        "status": "online",
        "service": "support-triage-ai",
        "endpoints": ["/triage", "/health"]
    }

@app.get("/health", summary="Health Check", tags=["General"])
def health_check():
    return {"status": "ok"}

@app.post("/triage", response_model=TriageResponse, summary="Triage Customer Support Message", tags=["AI Triage"])
async def triage_message(payload: TriageRequest):
    # Check Stub Mode (saves quota during development)
    if os.environ.get("LLM_STUB") == "1":
        return TriageResponse(
            category=CategoryEnum.BILLING,
            urgency=UrgencyEnum.NORMAL,
            confidence=0.95,
            reason="[STUB] Predefined classification for development testing."
        )

    # (Stage 2 will wire live model calls here)
    raise HTTPException(status_code=501, detail="Live LLM call will be wired in Stage 2")