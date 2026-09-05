import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
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

# 1. Initialize OpenAI-compatible Client
base_url = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")
api_key = os.environ.get("LLM_API_KEY", "")
model_name = os.environ.get("LLM_MODEL", "openrouter/free")

client = OpenAI(base_url=base_url, api_key=api_key)

# 2. Load Prompt Specification from File
PROMPT_FILE = Path(__file__).parent / "prompts" / "triage-v1.md"
with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# 3. Custom 400 Validation Handler
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
        "model": model_name,
        "endpoints": ["/triage", "/health"]
    }

@app.get("/health", summary="Health Check", tags=["General"])
def health_check():
    return {"status": "ok"}

@app.post("/triage", response_model=TriageResponse, summary="Triage Customer Support Message", tags=["AI Triage"])
async def triage_message(payload: TriageRequest):
    # Stub Mode Check
    if os.environ.get("LLM_STUB") == "1":
        return TriageResponse(
            category=CategoryEnum.BILLING,
            urgency=UrgencyEnum.NORMAL,
            confidence=0.95,
            reason="[STUB] Predefined classification for development testing."
        )

    # Live LLM Call (Stage 2)
    try:
        response = client.chat.completions.create(
            model=model_name,
            temperature=0.0, # Deterministic, zero creativity
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": payload.text}
            ]
        )
        
        raw_content = response.choices[0].message.content.strip()
        
        # Clean any surrounding markdown code fences if model returned them
        if raw_content.startswith("```"):
            lines = raw_content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_content = "\n".join(lines).strip()
            
        parsed_data = json.loads(raw_content)
        return TriageResponse(**parsed_data)

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"LLM call failed: {str(exc)}")